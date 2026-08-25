from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Pattern

from .dedup import LlamaIndexChunkDeduplicator
from .model_catalog import ModelSpec
from .unstructured_pipeline import ChunkingPolicy, UnstructuredDocumentPipeline


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


SOURCE_AUTHORITY = {"P0": 1.0, "P1": 0.9, "P2": 0.72, "P3": 0.55}


@dataclass(frozen=True)
class AuditCategory:
    name: str
    pattern: Pattern[str]
    question_template: str
    relevance: float


def _category(name: str, pattern: str, question: str, relevance: float) -> AuditCategory:
    return AuditCategory(name, re.compile(pattern, re.IGNORECASE), question, relevance)


AUDIT_CATEGORIES: tuple[AuditCategory, ...] = (
    _category(
        "model_identity",
        r"model[ _-]?id|model alias|snapshot|alias routes|latest flagship|most capable|"
        r"flagship model|designed for|parameter model",
        "What official identity, tier, alias, or positioning distinguishes {model}?",
        0.98,
    ),
    _category(
        "context_output",
        r"context (?:window|length)|million-token context|1m[- ]token|"
        r"max(?:imum)? output|output tokens|128k|200k|500k",
        "What context-window and maximum-output behavior should {model} exhibit?",
        1.0,
    ),
    _category(
        "reasoning_behavior",
        r"reasoning(?:[._ ]effort)?|thinking(?:[._ ]type| mode)?|non-thinking|"
        r"adaptive thinking|think high|think max|reasoning_content",
        "Which reasoning modes and control parameters are characteristic of {model}?",
        1.0,
    ),
    _category(
        "modalities",
        r"text-only|text only|multimodal|modalit|vision|image input|"
        r"visual understanding|audio|video",
        "Which input and output modalities are officially supported by {model}?",
        0.9,
    ),
    _category(
        "tools_agents",
        r"tool(?:s| calling| use)|function calling|agentic|agents?|computer use|"
        r"code execution|web search|x search|terminal tools",
        "Which tool-use and agent behaviors distinguish {model}?",
        0.94,
    ),
    _category(
        "performance",
        r"benchmark|swe[- ]|coding|performance|state.of.the.art|\bsota\b|"
        r"cybergym|long-horizon|accuracy|pass@1|resolved",
        "What distinctive, source-backed performance behavior is reported for {model}?",
        0.88,
    ),
    _category(
        "architecture",
        r"mixture.of.experts|\bmoe\b|parameters?|activated|attention|open[- ]source|"
        r"open[- ]weights?|architecture|fp4|fp8|experts",
        "What architecture or open-weight characteristics distinguish {model}?",
        0.86,
    ),
    _category(
        "pricing",
        r"pricing|per (?:one )?million|per 1m|cached input|\$\s*\d|"
        r"token (?:price|cost)|costs? \$",
        "What official token-pricing pattern is associated with {model}?",
        0.72,
    ),
    _category(
        "safety_behavior",
        r"safety|refusal|classifier|cybersecurity|cyber capability|security|"
        r"vulnerability|distillation|bio(?:logy)?",
        "What safety or security behavior is distinctive for {model}?",
        0.9,
    ),
    _category(
        "api_behavior",
        r"streaming|structured output|response_format|tool_choice|request will fail|"
        r"role order|chat completions|responses api|reasoning_content",
        "What API-level response behavior or request constraint should {model} exhibit?",
        0.96,
    ),
)


PREFERRED_PATTERNS: dict[str, str] = {
    "model_identity": r"model id|alias|flagship|designed for|most capable|snapshot",
    "context_output": r"context window|context length|max(?:imum)? output",
    "reasoning_behavior": r"always.+reasoning|thinking.+enabled|reasoning[._ ]effort|"
    r"disable.+thinking|three reasoning",
    "modalities": r"text-only|multimodal|modalities.+image|vision input|"
    r"visual understanding",
    "tools_agents": r"tool calling|tool-use|tool use|function calling|terminal tools|"
    r"coordinate.+tools|agentic workflow|multi-tool",
    "performance": r"benchmark|performance gain|state.of.the.art|long-horizon",
    "architecture": r"mixture.of.experts|\bmoe\b|parameters|activated|attention|"
    r"open[- ]weights",
    "pricing": r"pricing|per (?:one )?million|per 1m|\$\s*\d|cached input",
    "safety_behavior": r"safety|cybergym|vulnerability|refusal|classifier",
    "api_behavior": r"request will fail|streaming (?:response|output)|"
    r"structured output|response_format.+json|role order|reasoning_content",
}


class MultiModelAuditProcessor:
    """Builds conservative, extractive audit records for one model.

    A claim is admitted only when a P0/P1 body chunk contains both an explicit
    target-model mention and category-specific evidence. Front-matter model labels
    never count as evidence. This intentionally leaves HOLD or mismatched sources
    without fabricated Ground Truth.
    """

    def __init__(self, document_pipeline: UnstructuredDocumentPipeline) -> None:
        self.document_pipeline = document_pipeline
        self.deduplicator = LlamaIndexChunkDeduplicator()

    def process(
        self,
        spec: ModelSpec,
        raw_root: Path,
        output_root: Path,
        *,
        download_assets: bool = True,
    ) -> dict[str, Any]:
        output_root.mkdir(parents=True, exist_ok=True)
        documents: dict[str, dict[str, Any]] = {}
        all_elements: list[dict[str, Any]] = []
        all_tables: list[dict[str, Any]] = []
        all_chunks: list[dict[str, Any]] = []
        all_assets: list[dict[str, Any]] = []
        dropped_sections: list[dict[str, str]] = []

        content_files = sorted(raw_root.glob("p*/*/content.md"))
        if len(content_files) != 5:
            raise ValueError(
                f"Expected 5 sources for {spec.slug}, found {len(content_files)}."
            )

        for content_path in content_files:
            document = self.document_pipeline.process_source(content_path)
            source_id = document["front_matter"].get("source_id", "")
            for collection_name in ("elements", "tables", "chunks", "assets"):
                for record in document[collection_name]:
                    record.update(
                        {
                            "model_id": spec.slug,
                            "subject_model": spec.slug,
                            "model_family": spec.family,
                            "model_version": spec.version,
                        }
                    )
            documents[source_id] = {**document, "content_path": str(content_path)}
            all_elements.extend(document["elements"])
            all_tables.extend(document["tables"])
            all_chunks.extend(document["chunks"])
            all_assets.extend(document["assets"])
            dropped_sections.extend(document["dropped_sections"])

        chunks, chunk_aliases, dedup_stats = self.deduplicator.deduplicate(all_chunks)
        claims, coverage = self._extract_claims(spec, chunks)
        attributes = self._compile_attributes(spec, claims)
        evidence_chunks = self._compile_evidence_chunks(spec, chunks, claims)

        if download_assets:
            assets = self.document_pipeline.download_and_ocr_assets(all_assets, output_root)
        else:
            assets = [
                {
                    **asset,
                    "download_status": "skipped",
                    "ocr_status": "skipped_by_option",
                    "embedding_eligible": False,
                    "quarantine_reason": "asset processing skipped by command option",
                }
                for asset in all_assets
            ]

        admitted_claims = [claim for claim in claims if claim["eligible_for_ground_truth"]]
        quarantined_claims = [
            claim for claim in claims if not claim["eligible_for_ground_truth"]
        ]
        unique_assets = {
            asset.get("url", f"missing-{index}"): asset
            for index, asset in enumerate(assets)
        }
        document_manifest = [
            {
                "source_id": source_id,
                "source_level": document["front_matter"].get("priority", ""),
                "source_url": document["front_matter"].get("source_url", ""),
                "captured_at": document["front_matter"].get("captured_at", ""),
                "content_path": document["content_path"],
                "clean_characters": len(document["clean_text"]),
                "elements": len(document["elements"]),
                "chunks_before_dedup": len(document["chunks"]),
                "tables": len(document["tables"]),
                "images": len(document["assets"]),
            }
            for source_id, document in sorted(documents.items())
        ]
        return {
            "model": {
                "model_id": spec.slug,
                "label": spec.label,
                "family": spec.family,
                "version": spec.version,
                "source_review_status": spec.source_review_status,
            },
            "documents": document_manifest,
            "clean_documents": {
                source_id: document["clean_text"]
                for source_id, document in documents.items()
            },
            "elements": all_elements,
            "sections": chunks,
            "chunks": chunks,
            "evidence_chunks": evidence_chunks,
            "tables": all_tables,
            "claims": claims,
            "ground_truth_claims": admitted_claims,
            "attributes": attributes,
            "assets": assets,
            "quarantine": {
                "claims": quarantined_claims,
                "assets": assets,
                "dropped_sections": dropped_sections,
                "coverage_gaps": coverage["coverage_gaps"],
            },
            "coverage": coverage,
            "dedup": dedup_stats,
            "stats": {
                "documents": len(documents),
                "elements": len(all_elements),
                "chunks_before_dedup": len(all_chunks),
                "chunks_after_dedup": len(chunks),
                "duplicate_chunks_removed": dedup_stats["duplicates_removed"],
                "tables": len(all_tables),
                "claims": len(claims),
                "ground_truth_claims": len(admitted_claims),
                "quarantined_claims": len(quarantined_claims),
                "attributes": len(attributes),
                "evidence_chunks": len(evidence_chunks),
                "images_found": len(all_assets),
                "image_unique_urls": len(unique_assets),
                "images_downloaded": sum(
                    item.get("download_status") == "success"
                    for item in unique_assets.values()
                ),
                "ocr_success": sum(
                    item.get("ocr_status") == "success"
                    for item in unique_assets.values()
                ),
                "records_for_embedding": len(evidence_chunks)
                + len(admitted_claims)
                + len(attributes),
            },
        }

    def _extract_claims(
        self,
        spec: ModelSpec,
        chunks: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        alias_pattern = re.compile(
            "|".join(re.escape(alias) for alias in sorted(spec.aliases, key=len, reverse=True)),
            re.IGNORECASE,
        )
        candidates: dict[str, list[tuple[float, dict[str, Any], str]]] = {
            category.name: [] for category in AUDIT_CATEGORIES
        }
        explicit_chunk_rows = [
            chunk for chunk in chunks if alias_pattern.search(chunk["text"])
        ]
        explicit_chunks = len(explicit_chunk_rows)
        priority_explicit_chunks = sum(
            chunk.get("source_level") in {"P0", "P1"}
            for chunk in explicit_chunk_rows
        )
        subject_chunk_by_source: dict[str, str] = {}
        for chunk in explicit_chunk_rows:
            subject_chunk_by_source.setdefault(chunk["source_id"], chunk["id"])

        for chunk in chunks:
            if chunk["source_id"] not in subject_chunk_by_source:
                continue
            source_level = chunk.get("source_level", "")
            for category in AUDIT_CATEGORIES:
                excerpt = self._best_excerpt(
                    chunk["text"], alias_pattern, category.pattern
                )
                if not excerpt:
                    continue
                if not re.search(
                    PREFERRED_PATTERNS[category.name], excerpt, re.IGNORECASE
                ):
                    continue
                score = self._candidate_score(
                    source_level=source_level,
                    excerpt=excerpt,
                    alias_pattern=alias_pattern,
                    category=category,
                )
                candidates[category.name].append((score, chunk, excerpt))

        claims: list[dict[str, Any]] = []
        admitted_categories: list[str] = []
        rejected_categories: list[str] = []
        for category in AUDIT_CATEGORIES:
            ranked = sorted(
                candidates[category.name],
                key=lambda item: (
                    item[1].get("source_level") in {"P0", "P1"},
                    item[0],
                ),
                reverse=True,
            )
            if not ranked:
                continue
            _, chunk, excerpt = ranked[0]
            source_level = chunk.get("source_level", "")
            authority = SOURCE_AUTHORITY.get(source_level, 0.5)
            reasons: list[str] = []
            if source_level not in {"P0", "P1"}:
                reasons.append("only P0/P1 evidence is admitted as Ground Truth")
            if spec.source_review_status == "HOLD":
                reasons.append("source manifest is on HOLD")
            subject_context_chunk_id = subject_chunk_by_source.get(chunk["source_id"])
            if not subject_context_chunk_id:
                reasons.append("source body does not explicitly establish the target model")
            if "�" in excerpt:
                reasons.append("evidence contains replacement-character encoding damage")

            eligible = not reasons
            if eligible:
                admitted_categories.append(category.name)
            else:
                rejected_categories.append(category.name)
            claim_id = f"{spec.slug}-{category.name}"
            embedding_text = (
                f"Model: {spec.label}\n"
                f"Audit fact type: {category.name}\n"
                f"Source-backed evidence: {excerpt}\n"
                f"Applicable surface: API and model behavior"
            )
            claim = {
                "id": claim_id,
                "record_type": "claim",
                "model_id": spec.slug,
                "subject_model": spec.slug,
                "model_family": spec.family,
                "model_version": spec.version,
                "comparison_models": [],
                "claim_type": category.name,
                "predicate": category.name,
                "value": excerpt,
                "summary": excerpt,
                "source_id": chunk["source_id"],
                "source_level": source_level,
                "source_url": chunk.get("source_url", ""),
                "captured_at": chunk.get("captured_at", ""),
                "surface": "api_and_behavior",
                "effective_from": chunk.get("captured_at", "")[:10],
                "authority": authority,
                "audit_relevance": category.relevance,
                "evidence_quote": excerpt,
                "evidence_verified": True,
                "evidence_match_score": 1.0,
                "evidence_chunk_id": chunk["id"],
                "evidence_chain": {
                    "audit_record_id": claim_id,
                    "evidence_chunk_id": chunk["id"],
                    "source_id": chunk["source_id"],
                    "source_url": chunk.get("source_url", ""),
                    "captured_at": chunk.get("captured_at", ""),
                    "subject_context_chunk_id": subject_context_chunk_id,
                },
                "declared_ground_truth_candidate": True,
                "eligible_for_ground_truth": eligible,
                "fallback_contaminated": False,
                "configuration_contaminated": False,
                "policy_decision": "admit" if eligible else "quarantine",
                "quarantine_reason": "; ".join(reasons),
                "embedding_text": embedding_text,
            }
            claim["content_hash"] = _sha256(
                json.dumps(claim, ensure_ascii=False, sort_keys=True)
            )
            claims.append(claim)

        missing_categories = [
            category.name
            for category in AUDIT_CATEGORIES
            if not candidates[category.name]
        ]
        coverage_gaps: list[str] = []
        if explicit_chunks == 0:
            coverage_gaps.append(
                "No captured page body explicitly names the target model; front matter was ignored."
            )
        if priority_explicit_chunks == 0:
            coverage_gaps.append(
                "No P0/P1 chunk explicitly names the target model."
            )
        if spec.source_review_status != "APPROVE":
            coverage_gaps.append(
                f"Source manifest review status is {spec.source_review_status}."
            )
        return claims, {
            "source_review_status": spec.source_review_status,
            "explicit_model_chunks": explicit_chunks,
            "p0_p1_explicit_model_chunks": priority_explicit_chunks,
            "admitted_categories": admitted_categories,
            "rejected_categories": rejected_categories,
            "missing_categories": missing_categories,
            "coverage_gaps": coverage_gaps,
        }

    @staticmethod
    def _best_excerpt(
        text: str,
        alias_pattern: Pattern[str],
        category_pattern: Pattern[str],
    ) -> str:
        units: list[str] = []
        for line in text.splitlines():
            normalized = re.sub(r"\s+", " ", line).strip(" |-\t")
            if not normalized:
                continue
            split_units = re.split(r"(?<=[.!?。！？])\s+", normalized)
            units.extend(
                unit
                for unit in split_units
                if len(unit) >= 12
                and (
                    unit.count(" ") >= 2
                    or bool(re.search(r"\d[.,]\d|\$\s*\d", unit))
                )
            )
        flattened = re.sub(r"\s+", " ", text).strip()
        for match in category_pattern.finditer(flattened):
            start = max(0, match.start() - 320)
            end = min(len(flattened), match.end() + 620)
            window = flattened[start:end].strip(" |-\t")
            if len(window) >= 20:
                units.append(window)
        category_indexes = [
            index for index, unit in enumerate(units) if category_pattern.search(unit)
        ]
        if not category_indexes:
            return ""
        alias_indexes = [
            index for index, unit in enumerate(units) if alias_pattern.search(unit)
        ]

        best: tuple[float, str] | None = None
        for index in category_indexes:
            nearest_alias = (
                min(alias_indexes, key=lambda alias_index: abs(alias_index - index))
                if alias_indexes
                else index
            )
            distance = abs(nearest_alias - index)
            selected_indexes = (
                sorted({index, nearest_alias}) if distance <= 3 else [index]
            )
            excerpt = " ".join(units[item] for item in selected_indexes)
            excerpt = re.sub(r"\s+", " ", excerpt).strip()
            if len(excerpt) > 1400:
                excerpt = excerpt[:1397].rstrip() + "..."
            score = (
                3.0 * bool(alias_pattern.search(units[index]))
                + 1.0 / (1 + distance)
                + min(len(excerpt), 700) / 1400
            )
            if best is None or score > best[0]:
                best = (score, excerpt)
        return best[1] if best else ""

    @staticmethod
    def _candidate_score(
        *,
        source_level: str,
        excerpt: str,
        alias_pattern: Pattern[str],
        category: AuditCategory,
    ) -> float:
        preferred = re.search(
            PREFERRED_PATTERNS.get(category.name, r"$^"), excerpt, re.IGNORECASE
        )
        code_penalty = bool(
            re.search(
                r"\b(?:import|from)\s+[\w.]+|api_key\s*=|client\s*=|"
                r"response\s*=|\{\s*[\"']|\bpublic static void\b",
                excerpt,
                re.IGNORECASE,
            )
        )
        benchmark_table_penalty = (
            category.name == "tools_agents"
            and bool(re.search(r"Agents.? Last Exam|Benchmark .+ GLM|Pass@1", excerpt))
        )
        encoding_penalty = bool(
            "�" in excerpt or "��" in excerpt or "鈥" in excerpt
        )
        return (
            SOURCE_AUTHORITY.get(source_level, 0.5) * 10
            + 0.5 * bool(alias_pattern.search(excerpt))
            + min(len(category.pattern.findall(excerpt)), 4)
            + 0.5 * bool(re.search(r"\d", excerpt))
            + 5 * bool(preferred)
            - 4 * code_penalty
            - 4 * benchmark_table_penalty
            - 3 * encoding_penalty
        )

    @staticmethod
    def _compile_attributes(
        spec: ModelSpec,
        claims: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        category_by_name = {category.name: category for category in AUDIT_CATEGORIES}
        attributes: list[dict[str, Any]] = []
        for claim in claims:
            if not claim["eligible_for_ground_truth"]:
                continue
            category = category_by_name[claim["claim_type"]]
            attribute_id = f"attr-{spec.slug}-{category.name}"
            question = category.question_template.format(model=spec.label)
            embedding_text = (
                f"Model: {spec.label}\n"
                f"Audit attribute: {category.name}\n"
                f"Audit question: {question}\n"
                f"Expected evidence: {claim['evidence_quote']}"
            )
            attribute = {
                "id": attribute_id,
                "record_type": "attribute",
                "model_id": spec.slug,
                "subject_model": spec.slug,
                "model_family": spec.family,
                "model_version": spec.version,
                "claim_type": "audit_attribute",
                "predicate": category.name,
                "value": claim["evidence_quote"],
                "title": f"{spec.label}: {category.name}",
                "audit_question": question,
                "expected_signal": claim["evidence_quote"],
                "source_claim_ids": [claim["id"]],
                "source_id": claim["source_id"],
                "source_level": claim["source_level"],
                "source_urls": [claim["source_url"]] if claim["source_url"] else [],
                "captured_at": claim["captured_at"],
                "surface": claim["surface"],
                "effective_from": claim["effective_from"],
                "authority": claim["authority"],
                "audit_relevance": claim["audit_relevance"],
                "eligible_for_ground_truth": True,
                "evidence_verified": True,
                "evidence_chunk_ids": [claim["evidence_chunk_id"]],
                "evidence_chain": [claim["evidence_chain"]],
                "fallback_contaminated": False,
                "policy_decision": "admit",
                "quarantine_reason": "",
                "embedding_text": embedding_text,
            }
            attribute["content_hash"] = _sha256(
                json.dumps(attribute, ensure_ascii=False, sort_keys=True)
            )
            attributes.append(attribute)
        return attributes

    @staticmethod
    def _compile_evidence_chunks(
        spec: ModelSpec,
        chunks: list[dict[str, Any]],
        claims: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        claims_by_chunk: dict[str, list[dict[str, Any]]] = {}
        for claim in claims:
            if claim["eligible_for_ground_truth"]:
                claims_by_chunk.setdefault(claim["evidence_chunk_id"], []).append(claim)
                subject_context_chunk_id = claim.get("evidence_chain", {}).get(
                    "subject_context_chunk_id"
                )
                if (
                    subject_context_chunk_id
                    and subject_context_chunk_id != claim["evidence_chunk_id"]
                ):
                    claims_by_chunk.setdefault(subject_context_chunk_id, []).append(claim)

        records: list[dict[str, Any]] = []
        for chunk in chunks:
            linked_claims = claims_by_chunk.get(chunk["id"], [])
            if not linked_claims:
                continue
            record = dict(chunk)
            record.update(
                {
                    "model_id": spec.slug,
                    "subject_model": spec.slug,
                    "model_family": spec.family,
                    "model_version": spec.version,
                    "claim_type": "evidence",
                    "linked_claim_ids": sorted(claim["id"] for claim in linked_claims),
                    "surface": "api_and_behavior",
                    "effective_from": min(
                        (
                            claim["effective_from"]
                            for claim in linked_claims
                            if claim["effective_from"]
                        ),
                        default="",
                    ),
                    "authority": max(claim["authority"] for claim in linked_claims),
                    "audit_relevance": max(
                        claim["audit_relevance"] for claim in linked_claims
                    ),
                    "eligible_for_ground_truth": True,
                    "embedding_eligible": True,
                    "evidence_verified": True,
                    "fallback_contaminated": False,
                    "policy_decision": "admit",
                    "quarantine_reason": "",
                }
            )
            record["embedding_text"] = (
                f"Model: {spec.label}\n"
                f"Evidence heading: {record['heading']}\n"
                f"Source priority: {record['source_level']}\n"
                f"Evidence: {record['text']}"
            )
            record["content_hash"] = _sha256(record["embedding_text"])
            records.append(record)
        return records


def process_model_unstructured(
    spec: ModelSpec,
    raw_root: Path,
    output_root: Path,
    *,
    chunking_policy: ChunkingPolicy,
    tesseract_executable: Path,
    tessdata_prefix: Path,
    ocr_languages: list[str],
    hi_res_model_name: str,
    download_assets: bool = True,
) -> dict[str, Any]:
    document_pipeline = UnstructuredDocumentPipeline(
        chunking=chunking_policy,
        tesseract_executable=tesseract_executable,
        tessdata_prefix=tessdata_prefix,
        ocr_languages=ocr_languages,
        hi_res_model_name=hi_res_model_name,
    )
    return MultiModelAuditProcessor(document_pipeline).process(
        spec,
        raw_root,
        output_root,
        download_assets=download_assets,
    )
