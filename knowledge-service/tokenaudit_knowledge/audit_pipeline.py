from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .dedup import LlamaIndexChunkDeduplicator
from .processor import CLAIM_SPECS, ClaimSpec, _build_attributes, _find_evidence, _sha256
from .unstructured_pipeline import ChunkingPolicy, UnstructuredDocumentPipeline


class MetadataNormalizer:
    def normalize(
        self,
        spec: ClaimSpec,
        document: dict[str, Any],
    ) -> dict[str, Any]:
        metadata = document["front_matter"]
        return {
            "id": spec.claim_id,
            "record_type": "claim",
            "model_id": "claude-fable-5",
            "subject_model": "claude-fable-5",
            "model_family": "claude",
            "model_version": "5",
            "comparison_models": list(spec.comparison_models),
            "claim_type": spec.claim_type,
            "predicate": spec.predicate,
            "value": spec.value,
            "summary_zh": spec.summary_zh,
            "source_id": spec.source_id,
            "source_level": metadata.get("priority", ""),
            "source_url": metadata.get("source_url", ""),
            "captured_at": metadata.get("captured_at", ""),
            "capture_provider": metadata.get("capture_provider", ""),
            "surface": spec.surface,
            "effective_from": spec.effective_from,
            "authority": spec.authority,
            "audit_relevance": spec.audit_relevance,
            "declared_ground_truth_candidate": spec.eligible_for_ground_truth,
            "fallback_contaminated": spec.fallback_contaminated,
            "configuration_contaminated": False,
            "evidence_verified": False,
            "eligible_for_ground_truth": False,
            "quarantine_reason": spec.quarantine_reason,
        }


class ClaimValidator:
    def validate(
        self,
        claim: dict[str, Any],
        spec: ClaimSpec,
        document: dict[str, Any],
        chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        evidence = _find_evidence(document["clean_text"], spec.evidence_pattern)
        candidates = [
            chunk for chunk in chunks if spec.source_id in chunk.get("source_ids", [])
        ]
        best_chunk, score = self._best_chunk(evidence, candidates)
        verified = best_chunk is not None and score >= 0.65
        claim.update(
            {
                "evidence_quote": evidence,
                "evidence_verified": verified,
                "evidence_match_score": round(score, 6),
                "evidence_chunk_id": best_chunk["id"] if best_chunk else None,
                "evidence_chain": (
                    {
                        "audit_record_id": claim["id"],
                        "evidence_chunk_id": best_chunk["id"],
                        "source_id": spec.source_id,
                        "source_url": claim["source_url"],
                        "captured_at": claim["captured_at"],
                    }
                    if best_chunk
                    else None
                ),
            }
        )
        return claim

    @classmethod
    def _best_chunk(
        cls,
        evidence: str,
        chunks: list[dict[str, Any]],
    ) -> tuple[dict[str, Any] | None, float]:
        if not chunks:
            return None, 0.0
        evidence_normalized = cls._normalize(evidence)
        evidence_tokens = set(evidence_normalized.lower().split())
        best: dict[str, Any] | None = None
        best_score = 0.0
        for chunk in chunks:
            chunk_normalized = cls._normalize(chunk["text"])
            if evidence_normalized in chunk_normalized:
                score = 1.0
            else:
                chunk_tokens = set(chunk_normalized.lower().split())
                coverage = (
                    len(evidence_tokens & chunk_tokens) / len(evidence_tokens)
                    if evidence_tokens
                    else 0.0
                )
                sequence = SequenceMatcher(
                    None,
                    evidence_normalized[:2000],
                    chunk_normalized[:4000],
                ).ratio()
                score = 0.75 * coverage + 0.25 * sequence
            if score > best_score:
                best = chunk
                best_score = score
        return best, best_score

    @staticmethod
    def _normalize(text: str) -> str:
        text = re.sub(r"[`*_#|>\[\]()]", " ", text)
        return re.sub(r"\s+", " ", text).strip()


class ContaminationDetector:
    def inspect(self, claim: dict[str, Any]) -> dict[str, Any]:
        evidence = claim.get("evidence_quote", "").lower()
        mixed_benchmark = (
            claim["source_id"] == "04-artificial-analysis"
            and "fallback" in evidence
        )
        claim["configuration_contaminated"] = mixed_benchmark
        claim["fallback_contaminated"] = bool(
            claim["fallback_contaminated"] or mixed_benchmark
        )
        claim["contamination_signals"] = [
            signal
            for signal, present in (
                ("fallback_mixed_benchmark", mixed_benchmark),
                ("secondary_source", claim["source_level"] == "P3"),
                (
                    "marketing_without_reproducible_harness",
                    claim["claim_type"] == "performance_claim"
                    and claim["source_id"] == "01-anthropic-fable",
                ),
            )
            if present
        ]
        return claim


class GroundTruthPolicy:
    MIN_AUTHORITY = 0.8
    MIN_AUDIT_RELEVANCE = 0.2

    def decide(self, claim: dict[str, Any]) -> dict[str, Any]:
        reasons: list[str] = []
        if not claim["declared_ground_truth_candidate"]:
            reasons.append(claim["quarantine_reason"] or "claim not approved by audit policy")
        if not claim["evidence_verified"]:
            reasons.append("claim could not be traced to one Unstructured evidence chunk")
        if claim["fallback_contaminated"]:
            reasons.append("fallback or mixed-model configuration contaminates the evidence")
        if claim["authority"] < self.MIN_AUTHORITY:
            reasons.append("source authority below Ground Truth threshold")
        if claim["audit_relevance"] < self.MIN_AUDIT_RELEVANCE:
            reasons.append("fact is not sufficiently related to model behavior")

        claim["eligible_for_ground_truth"] = not reasons
        claim["policy_decision"] = "admit" if not reasons else "quarantine"
        claim["quarantine_reason"] = "; ".join(dict.fromkeys(reasons))
        claim["embedding_text"] = (
            "模型：Claude Fable 5\n"
            f"模型版本：{claim['model_version']}\n"
            f"事实类型：{claim['claim_type']}\n"
            f"结论：{claim['summary_zh']}\n"
            f"适用 API 表面：{claim['surface']}\n"
            f"原文证据：{claim.get('evidence_quote', '')}"
        )
        claim["content_hash"] = _sha256(
            json.dumps(
                {key: value for key, value in claim.items() if key != "content_hash"},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return claim


class AuditAttributeCompiler:
    def compile(self, claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
        attributes = _build_attributes(claims)
        claims_by_id = {claim["id"]: claim for claim in claims}
        for attribute in attributes:
            source_claims = [
                claims_by_id[claim_id] for claim_id in attribute["source_claim_ids"]
            ]
            evidence_chains = [
                claim["evidence_chain"]
                for claim in source_claims
                if claim.get("evidence_chain")
            ]
            attribute.update(
                {
                    "model_family": "claude",
                    "model_version": "5",
                    "captured_at": max(
                        (claim.get("captured_at", "") for claim in source_claims),
                        default="",
                    ),
                    "evidence_verified": all(
                        claim["evidence_verified"] for claim in source_claims
                    ),
                    "evidence_chunk_ids": sorted(
                        {
                            claim["evidence_chunk_id"]
                            for claim in source_claims
                            if claim.get("evidence_chunk_id")
                        }
                    ),
                    "evidence_chain": evidence_chains,
                    "policy_decision": "admit",
                    "quarantine_reason": "",
                }
            )
            attribute["content_hash"] = _sha256(
                json.dumps(
                    {key: value for key, value in attribute.items() if key != "content_hash"},
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        return attributes


class Fable5AuditProcessor:
    def __init__(
        self,
        document_pipeline: UnstructuredDocumentPipeline,
    ) -> None:
        self.document_pipeline = document_pipeline
        self.metadata_normalizer = MetadataNormalizer()
        self.claim_validator = ClaimValidator()
        self.contamination_detector = ContaminationDetector()
        self.ground_truth_policy = GroundTruthPolicy()
        self.attribute_compiler = AuditAttributeCompiler()
        self.deduplicator = LlamaIndexChunkDeduplicator()

    def process(
        self,
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
            raise ValueError(f"Expected 5 Fable 5 sources, found {len(content_files)}.")

        for content_path in content_files:
            document = self.document_pipeline.process_source(content_path)
            source_id = document["front_matter"].get("source_id", "")
            documents[source_id] = {
                **document,
                "content_path": str(content_path),
            }
            all_elements.extend(document["elements"])
            all_tables.extend(document["tables"])
            all_chunks.extend(document["chunks"])
            all_assets.extend(document["assets"])
            dropped_sections.extend(document["dropped_sections"])

        chunks, chunk_aliases, dedup_stats = self.deduplicator.deduplicate(all_chunks)
        claims: list[dict[str, Any]] = []
        for spec in CLAIM_SPECS:
            document = documents[spec.source_id]
            claim = self.metadata_normalizer.normalize(spec, document)
            claim = self.claim_validator.validate(claim, spec, document, chunks)
            if claim.get("evidence_chunk_id"):
                claim["evidence_chunk_id"] = chunk_aliases.get(
                    claim["evidence_chunk_id"], claim["evidence_chunk_id"]
                )
                if claim.get("evidence_chain"):
                    claim["evidence_chain"]["evidence_chunk_id"] = claim[
                        "evidence_chunk_id"
                    ]
            claim = self.contamination_detector.inspect(claim)
            claim = self.ground_truth_policy.decide(claim)
            claims.append(claim)

        ground_truth_claims = [
            claim for claim in claims if claim["eligible_for_ground_truth"]
        ]
        attributes = self.attribute_compiler.compile(claims)
        evidence_chunks = self._compile_evidence_chunks(chunks, ground_truth_claims)
        processed_assets = (
            self.document_pipeline.download_and_ocr_assets(all_assets, output_root)
            if download_assets
            else []
        )
        unique_assets_by_url = {
            asset["url"]: asset for asset in processed_assets if asset.get("url")
        }
        unique_assets = list(unique_assets_by_url.values())

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
            "ground_truth_claims": ground_truth_claims,
            "attributes": attributes,
            "assets": processed_assets,
            "quarantine": {
                "claims": [
                    claim for claim in claims if not claim["eligible_for_ground_truth"]
                ],
                "assets": processed_assets,
                "dropped_sections": dropped_sections,
            },
            "dedup": dedup_stats,
            "stats": {
                "documents": len(documents),
                "elements": len(all_elements),
                "chunks_before_dedup": len(all_chunks),
                "chunks_after_dedup": len(chunks),
                "duplicate_chunks_removed": dedup_stats["duplicates_removed"],
                "tables": len(all_tables),
                "claims": len(claims),
                "ground_truth_claims": len(ground_truth_claims),
                "quarantined_claims": len(claims) - len(ground_truth_claims),
                "attributes": len(attributes),
                "images_found": len(all_assets),
                "image_unique_urls": len({asset["url"] for asset in all_assets}),
                "images_processed": sum(
                    asset.get("role") != "decorative_or_unlabelled_image"
                    for asset in unique_assets
                ),
                "images_downloaded": sum(
                    asset.get("download_status") == "success" for asset in unique_assets
                ),
                "ocr_success": sum(
                    asset.get("ocr_status") == "success" for asset in unique_assets
                ),
                "ocr_empty": sum(
                    asset.get("ocr_status") == "empty" for asset in unique_assets
                ),
                "ocr_failed": sum(
                    asset.get("ocr_status") == "failed" for asset in unique_assets
                ),
                "ocr_skipped": sum(
                    str(asset.get("ocr_status", "")).startswith("skipped")
                    for asset in unique_assets
                ),
                "evidence_chunks": len(evidence_chunks),
                "records_for_embedding": len(evidence_chunks)
                + len(ground_truth_claims)
                + len(attributes),
            },
        }

    @staticmethod
    def _compile_evidence_chunks(
        chunks: list[dict[str, Any]],
        claims: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        claims_by_chunk: dict[str, list[dict[str, Any]]] = {}
        for claim in claims:
            chunk_id = claim.get("evidence_chunk_id")
            if chunk_id:
                claims_by_chunk.setdefault(chunk_id, []).append(claim)

        records: list[dict[str, Any]] = []
        for chunk in chunks:
            linked_claims = claims_by_chunk.get(chunk["id"], [])
            if not linked_claims:
                continue
            record = dict(chunk)
            record.update(
                {
                    "claim_type": "evidence",
                    "linked_claim_ids": sorted(claim["id"] for claim in linked_claims),
                    "surface": (
                        linked_claims[0]["surface"]
                        if len({claim["surface"] for claim in linked_claims}) == 1
                        else "mixed"
                    ),
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
                "模型：Claude Fable 5\n"
                f"证据章节：{record['heading']}\n"
                f"来源等级：{record['source_level']}\n"
                f"证据正文：{record['text']}"
            )
            record["content_hash"] = _sha256(record["embedding_text"])
            records.append(record)
        return records


def process_fable5_unstructured(
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
    return Fable5AuditProcessor(document_pipeline).process(
        raw_root,
        output_root,
        download_assets=download_assets,
    )
