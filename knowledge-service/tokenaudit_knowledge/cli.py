from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .audit_pipeline import process_fable5_unstructured
from .config import KnowledgeSettings
from .embedding import VoyageEmbeddingClient
from .milvus_store import KnowledgeMilvusStore
from .mixed_rag_eval import run_mixed_rag_test
from .model_catalog import remaining_model_specs
from .multi_model_pipeline import process_model_unstructured
from .rag_eval import run_fable5_rag_test
from .rerank import VoyageRerankClient
from .unstructured_pipeline import ChunkingPolicy


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _settings(args: argparse.Namespace) -> KnowledgeSettings:
    return KnowledgeSettings.load(args.env_file)


def _embedding_client(settings: KnowledgeSettings) -> VoyageEmbeddingClient:
    return VoyageEmbeddingClient(
        base_url=settings.embedding_base_url,
        api_key=settings.embedding_api_key,
        model=settings.embedding_model,
        dimension=settings.embedding_dimension,
        timeout_seconds=settings.embedding_timeout_seconds,
        min_request_interval_seconds=float(
            os.environ.get("VOYAGE_MIN_REQUEST_INTERVAL_SECONDS", "0")
        ),
    )


def _store(settings: KnowledgeSettings) -> KnowledgeMilvusStore:
    return KnowledgeMilvusStore(
        uri=settings.milvus_uri,
        token=settings.milvus_token,
        database=settings.milvus_database,
        collection=settings.milvus_collection,
        dimension=settings.embedding_dimension,
        metric_type=settings.milvus_metric_type,
    )


def _reranker(settings: KnowledgeSettings) -> VoyageRerankClient:
    return VoyageRerankClient(
        base_url=settings.rerank_base_url,
        api_key=settings.rerank_api_key,
        model=settings.rerank_model,
        timeout_seconds=settings.rerank_timeout_seconds,
        min_request_interval_seconds=float(
            os.environ.get("VOYAGE_MIN_REQUEST_INTERVAL_SECONDS", "0")
        ),
    )


def _process_and_write(settings: KnowledgeSettings) -> dict[str, Any]:
    chunking = ChunkingPolicy(
        max_characters=settings.chunk_max_characters,
        new_after_n_characters=settings.chunk_new_after_characters,
        combine_text_under_n_characters=settings.chunk_combine_under_characters,
        overlap_characters=settings.chunk_overlap_characters,
    )
    result = process_fable5_unstructured(
        settings.raw_source_root,
        settings.processed_root,
        chunking_policy=chunking,
        tesseract_executable=settings.tesseract_executable,
        tessdata_prefix=settings.tessdata_prefix,
        ocr_languages=list(settings.ocr_languages),
        hi_res_model_name=settings.unstructured_hi_res_model,
    )
    output = settings.processed_root
    clean_root = output / "clean"
    clean_root.mkdir(parents=True, exist_ok=True)
    for source_id, text in result["clean_documents"].items():
        (clean_root / f"{source_id}.md").write_text(text, encoding="utf-8")
    _write_jsonl(output / "elements.jsonl", result["elements"])
    _write_jsonl(output / "sections.jsonl", result["sections"])
    _write_jsonl(output / "chunks.jsonl", result["chunks"])
    _write_jsonl(output / "evidence-chunks.jsonl", result["evidence_chunks"])
    _write_jsonl(output / "tables.jsonl", result["tables"])
    _write_jsonl(output / "claims.jsonl", result["claims"])
    _write_jsonl(output / "ground-truth-claims.jsonl", result["ground_truth_claims"])
    _write_jsonl(output / "attributes.jsonl", result["attributes"])
    _write_jsonl(output / "assets.jsonl", result["assets"])
    _write_json(output / "quarantine.json", result["quarantine"])
    _write_json(
        output / "processing-manifest.json",
        {
            "schema_version": 2,
            "model_id": "claude-fable-5",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": {
                "partition_and_noise_filter": "unstructured",
                "document_structure": "unstructured elements",
                "ocr_and_image_structure": "unstructured hi_res/ocr_only",
                "table_parser": "unstructured Table + text_as_html",
                "chunker": "unstructured chunk_by_title",
                "deduplicator": "llama-index-core DocstoreStrategy.DUPLICATES_ONLY",
                "embedding": "voyage",
                "rerank": "voyage",
            },
            "chunking_policy": {
                "strategy": "by_title",
                "max_characters": settings.chunk_max_characters,
                "new_after_n_characters": settings.chunk_new_after_characters,
                "combine_text_under_n_characters": settings.chunk_combine_under_characters,
                "overlap_characters": settings.chunk_overlap_characters,
                "overlap_all": False,
                "isolate_table": True,
            },
            "retrieval_policy": {
                "vector_top_k": settings.retrieval_top_k,
                "rerank_top_k": settings.rerank_top_k,
                "rerank_model": settings.rerank_model,
            },
            "embedding_policy": "verified_evidence_chunks_claims_and_attributes",
            "raw_sections_embedded": False,
            "fallback_contaminated_records_embedded": False,
            "stats": result["stats"],
            "documents": result["documents"],
            "dedup": result["dedup"],
        },
    )
    return result


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_generic_result(
    settings: KnowledgeSettings,
    result: dict[str, Any],
    output: Path,
) -> None:
    clean_root = output / "clean"
    clean_root.mkdir(parents=True, exist_ok=True)
    for source_id, content in result["clean_documents"].items():
        (clean_root / f"{source_id}.md").write_text(content, encoding="utf-8")
    for filename, key in (
        ("elements.jsonl", "elements"),
        ("sections.jsonl", "sections"),
        ("chunks.jsonl", "chunks"),
        ("evidence-chunks.jsonl", "evidence_chunks"),
        ("tables.jsonl", "tables"),
        ("claims.jsonl", "claims"),
        ("ground-truth-claims.jsonl", "ground_truth_claims"),
        ("attributes.jsonl", "attributes"),
        ("assets.jsonl", "assets"),
    ):
        _write_jsonl(output / filename, result[key])
    _write_json(output / "quarantine.json", result["quarantine"])
    _write_json(
        output / "processing-manifest.json",
        {
            "schema_version": 3,
            "model": result["model"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": {
                "partition_and_noise_filter": "unstructured",
                "document_structure": "unstructured elements",
                "ocr_and_image_structure": "unstructured hi_res/ocr_only",
                "table_parser": "unstructured Table + text_as_html",
                "chunker": "unstructured chunk_by_title",
                "deduplicator": "llama-index-core DocstoreStrategy.DUPLICATES_ONLY",
                "claim_policy": "extractive P0/P1 target-model evidence only",
                "embedding": "voyage",
                "rerank": "voyage",
            },
            "chunking_policy": {
                "strategy": "by_title",
                "max_characters": settings.chunk_max_characters,
                "new_after_n_characters": settings.chunk_new_after_characters,
                "combine_text_under_n_characters": settings.chunk_combine_under_characters,
                "overlap_characters": settings.chunk_overlap_characters,
                "overlap_all": False,
                "isolate_table": True,
            },
            "retrieval_policy": {
                "vector_top_k": settings.retrieval_top_k,
                "rerank_top_k": settings.rerank_top_k,
                "rerank_model": settings.rerank_model,
            },
            "coverage": result["coverage"],
            "stats": result["stats"],
            "documents": result["documents"],
            "dedup": result["dedup"],
        },
    )


def _repair_fable_embedding_records(
    processed_root: Path,
) -> list[dict[str, Any]]:
    evidence = _read_jsonl(processed_root / "evidence-chunks.jsonl")
    claims = _read_jsonl(processed_root / "ground-truth-claims.jsonl")
    attributes = _read_jsonl(processed_root / "attributes.jsonl")
    claims_by_id = {claim["id"]: claim for claim in claims}

    for record in evidence:
        record["embedding_text"] = (
            "Model: Claude Fable 5\n"
            f"Evidence heading: {record.get('heading', '')}\n"
            f"Source priority: {record.get('source_level', '')}\n"
            f"Evidence: {record.get('text', '')}"
        )
    for record in claims:
        record["embedding_text"] = (
            "Model: Claude Fable 5\n"
            f"Audit fact type: {record.get('claim_type', '')}\n"
            f"Source-backed evidence: {record.get('evidence_quote', '')}\n"
            f"Applicable surface: {record.get('surface', '')}"
        )
    for record in attributes:
        supporting_evidence = " ".join(
            claims_by_id.get(claim_id, {}).get("evidence_quote", "")
            for claim_id in record.get("source_claim_ids", [])
        ).strip()
        record["embedding_text"] = (
            "Model: Claude Fable 5\n"
            f"Audit attribute ID: {record['id']}\n"
            f"Expected source-backed evidence: {supporting_evidence}"
        )
    for record in [*evidence, *claims, *attributes]:
        record["content_hash"] = hashlib.sha256(
            record["embedding_text"].encode("utf-8")
        ).hexdigest()
    return [*evidence, *claims, *attributes]


def ingest_all_models(args: argparse.Namespace) -> int:
    settings = _settings(args)
    chunking = ChunkingPolicy(
        max_characters=settings.chunk_max_characters,
        new_after_n_characters=settings.chunk_new_after_characters,
        combine_text_under_n_characters=settings.chunk_combine_under_characters,
        overlap_characters=settings.chunk_overlap_characters,
    )
    raw_base = settings.project_root / "docs" / "rag" / "raw-sources"
    processed_base = settings.project_root / "docs" / "rag" / "processed"
    combined_root = processed_base / "all-models"
    combined_root.mkdir(parents=True, exist_ok=True)

    fable_root = processed_base / "claude-fable-5"
    combined_records = _repair_fable_embedding_records(fable_root)
    fable_manifest = json.loads(
        (fable_root / "processing-manifest.json").read_text(encoding="utf-8")
    )
    model_coverage: list[dict[str, Any]] = [
        {
            "model_id": "claude-fable-5",
            "source_review_status": "APPROVE",
            "records": len(combined_records),
            "claims": len(
                [item for item in combined_records if item["record_type"] == "claim"]
            ),
            "attributes": len(
                [item for item in combined_records if item["record_type"] == "attribute"]
            ),
            "coverage_gaps": [],
        }
    ]

    for spec in remaining_model_specs():
        output_root = processed_base / spec.slug
        if args.reuse_processed:
            records = (
                _read_jsonl(output_root / "evidence-chunks.jsonl")
                + _read_jsonl(output_root / "ground-truth-claims.jsonl")
                + _read_jsonl(output_root / "attributes.jsonl")
            )
            processed_manifest = json.loads(
                (output_root / "processing-manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            coverage = processed_manifest["coverage"]
            stats = processed_manifest["stats"]
            ground_truth_claims = [
                record for record in records if record["record_type"] == "claim"
            ]
            attributes = [
                record for record in records if record["record_type"] == "attribute"
            ]
        else:
            result = process_model_unstructured(
                spec,
                raw_base / spec.slug,
                output_root,
                chunking_policy=chunking,
                tesseract_executable=settings.tesseract_executable,
                tessdata_prefix=settings.tessdata_prefix,
                ocr_languages=list(settings.ocr_languages),
                hi_res_model_name=settings.unstructured_hi_res_model,
                download_assets=not args.skip_assets,
            )
            _write_generic_result(settings, result, output_root)
            records = (
                result["evidence_chunks"]
                + result["ground_truth_claims"]
                + result["attributes"]
            )
            coverage = result["coverage"]
            stats = result["stats"]
            ground_truth_claims = result["ground_truth_claims"]
            attributes = result["attributes"]
        combined_records.extend(records)
        model_coverage.append(
            {
                "model_id": spec.slug,
                "source_review_status": spec.source_review_status,
                "records": len(records),
                "claims": len(ground_truth_claims),
                "attributes": len(attributes),
                "coverage_gaps": coverage["coverage_gaps"],
                "stats": stats,
            }
        )
        print(
            json.dumps(
                {
                    "stage": "processed",
                    "model_id": spec.slug,
                    "records": len(records),
                    "coverage_gaps": coverage["coverage_gaps"],
                },
                ensure_ascii=False,
            )
        )

    ids = [record["id"] for record in combined_records]
    if len(ids) != len(set(ids)):
        duplicate_ids = sorted({record_id for record_id in ids if ids.count(record_id) > 1})
        raise ValueError(f"Duplicate combined record IDs: {duplicate_ids[:10]}")
    _write_jsonl(combined_root / "combined-records.jsonl", combined_records)

    embedding = _embedding_client(settings)
    vectors = embedding.embed_documents(
        [record["embedding_text"] for record in combined_records]
    )
    store = _store(settings)
    upsert_count = 0
    try:
        store.ensure_collection(rebuild=args.rebuild)
        for start in range(0, len(combined_records), 64):
            batch_records = combined_records[start : start + 64]
            batch_vectors = vectors[start : start + 64]
            upsert_result = store.upsert_records(batch_records, batch_vectors)
            upsert_count += int(
                upsert_result.get("upsert_count", len(batch_records))
            )
        rows = store.query_all()
        _write_jsonl(combined_root / "milvus-export.jsonl", rows)
        manifest = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "models_requested": 10,
            "models_with_records": len(
                [item for item in model_coverage if item["records"] > 0]
            ),
            "records": len(combined_records),
            "record_types": {
                record_type: sum(
                    record["record_type"] == record_type
                    for record in combined_records
                )
                for record_type in ("evidence_chunk", "claim", "attribute")
            },
            "embedding": {
                "provider_endpoint": settings.embedding_base_url,
                "model": settings.embedding_model,
                "dimension": settings.embedding_dimension,
                "records": len(combined_records),
            },
            "milvus": {
                "uri": settings.milvus_uri,
                "collection": settings.milvus_collection,
                "metric_type": settings.milvus_metric_type,
                "upsert_count": upsert_count,
                "rows_after_upsert": len(rows),
            },
            "fable_source_manifest": str(fable_root / "processing-manifest.json"),
            "coverage": model_coverage,
        }
        _write_json(combined_root / "combined-processing-manifest.json", manifest)
        print(
            json.dumps(
                {
                    "stage": "ingested",
                    "records": len(combined_records),
                    "milvus_rows": len(rows),
                    "collection": settings.milvus_collection,
                    "models_with_records": manifest["models_with_records"],
                },
                ensure_ascii=False,
            )
        )
    finally:
        store.close()
    return 0


def test_mixed_rag(args: argparse.Namespace) -> int:
    settings = _settings(args)
    combined_root = settings.project_root / "docs" / "rag" / "processed" / "all-models"
    records = _read_jsonl(combined_root / "combined-records.jsonl")
    manifest = json.loads(
        (combined_root / "combined-processing-manifest.json").read_text(
            encoding="utf-8"
        )
    )
    store = _store(settings)
    try:
        report = run_mixed_rag_test(
            embedding=_embedding_client(settings),
            reranker=_reranker(settings),
            store=store,
            records=records,
            model_coverage=manifest["coverage"],
            retrieval_top_k=settings.retrieval_top_k,
            rerank_top_k=settings.rerank_top_k,
            output_root=combined_root,
        )
        print(json.dumps(report["metrics"], ensure_ascii=False, sort_keys=True))
    finally:
        store.close()
    return 0


def ingest_fable5(args: argparse.Namespace) -> int:
    settings = _settings(args)
    result = _process_and_write(settings)
    records = (
        result["evidence_chunks"]
        + result["ground_truth_claims"]
        + result["attributes"]
    )
    embedding = _embedding_client(settings)
    vectors = embedding.embed_documents([record["embedding_text"] for record in records])
    store = _store(settings)
    try:
        store.ensure_collection(rebuild=args.rebuild)
        upsert_result = store.upsert_records(records, vectors)
        rows = store.query_all("claude-fable-5")
        manifest = json.loads(
            (settings.processed_root / "processing-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        manifest.update(
            {
                "embedding": {
                    "provider_endpoint": settings.embedding_base_url,
                    "model": settings.embedding_model,
                    "dimension": settings.embedding_dimension,
                    "records": len(records),
                },
                "milvus": {
                    "uri": settings.milvus_uri,
                    "collection": settings.milvus_collection,
                    "metric_type": settings.milvus_metric_type,
                    "upsert_count": upsert_result.get("upsert_count", len(records)),
                    "rows_after_upsert": len(rows),
                },
            }
        )
        _write_json(settings.processed_root / "processing-manifest.json", manifest)
        print(
            json.dumps(
                {
                    "processed": result["stats"],
                    "embedded": len(records),
                    "milvus_rows": len(rows),
                    "collection": settings.milvus_collection,
                    "milvus_uri": settings.milvus_uri,
                },
                ensure_ascii=False,
            )
        )
    finally:
        store.close()
    return 0


def _vector_norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def review_fable5(args: argparse.Namespace) -> int:
    settings = _settings(args)
    embedding = _embedding_client(settings)
    store = _store(settings)
    queries = [
        (
            "安全分类器触发时 Claude Fable 5 API 返回什么状态码和 stop_reason？",
            "attr-fable5-refusal-protocol",
            {"attr-fable5-refusal-protocol", "fable5-refusal-protocol"},
        ),
        (
            "Claude Fable 5 能否关闭思考，应该怎样控制推理深度？",
            "attr-fable5-adaptive-thinking",
            {"attr-fable5-adaptive-thinking", "fable5-adaptive-thinking"},
        ),
        (
            "Claude Fable 5 会不会返回原始思维链？",
            "attr-fable5-thinking-visibility",
            {"attr-fable5-thinking-visibility", "fable5-thinking-visibility"},
        ),
        (
            "如何区分 Fable 5 官方回退到 Opus 4.8 与中转站偷偷换模型？",
            "attr-fable5-fallback-disambiguation",
            {
                "attr-fable5-fallback-disambiguation",
                "fable5-fallback-modes",
                "fable5-opus-fallback",
            },
        ),
        (
            "Fable 5 支持哪些复杂工具和 Agent 能力？",
            "attr-fable5-tools",
            {"attr-fable5-tools", "fable5-supported-features"},
        ),
        (
            "Fable 5 的上下文窗口和最大输出 Token 是多少？",
            "attr-fable5-context-output",
            {"attr-fable5-context-output", "fable5-context-output"},
        ),
    ]
    try:
        store.load_collection()
        rows = store.query_all("claude-fable-5")
        duplicate_hashes = sorted(
            {
                row["content_hash"]
                for row in rows
                if sum(other["content_hash"] == row["content_hash"] for other in rows) > 1
            }
        )
        invalid_rows = [
            row
            for row in rows
            if not row["eligible"] or row["fallback_contaminated"]
        ]
        exports = []
        for row in rows:
            payload = json.loads(row.pop("payload_json"))
            exports.append({**row, "payload": payload})
        _write_jsonl(settings.processed_root / "milvus-export.jsonl", exports)

        search_results = []
        top1_matches = 0
        semantic_top1_matches = 0
        attribute_recall_at_5 = 0
        query_vectors = embedding.embed_queries([query for query, _, _ in queries])
        for (query, expected_id, acceptable_top_ids), query_vector in zip(
            queries, query_vectors, strict=True
        ):
            hits = store.search(query_vector, limit=5)
            top_ids = [hit["entity"]["id"] for hit in hits]
            if top_ids and top_ids[0] == expected_id:
                top1_matches += 1
            if top_ids and top_ids[0] in acceptable_top_ids:
                semantic_top1_matches += 1
            if expected_id in top_ids:
                attribute_recall_at_5 += 1
            search_results.append(
                {
                    "query": query,
                    "expected_top_id": expected_id,
                    "acceptable_semantic_top_ids": sorted(acceptable_top_ids),
                    "semantic_top1_match": bool(
                        top_ids and top_ids[0] in acceptable_top_ids
                    ),
                    "expected_attribute_rank": (
                        top_ids.index(expected_id) + 1 if expected_id in top_ids else None
                    ),
                    "query_vector_dimension": len(query_vector),
                    "query_vector_norm": round(_vector_norm(query_vector), 6),
                    "hits": [
                        {
                            "rank": index + 1,
                            "id": hit["entity"]["id"],
                            "record_type": hit["entity"]["record_type"],
                            "claim_type": hit["entity"]["claim_type"],
                            "source_id": hit["entity"]["source_id"],
                            "distance": round(float(hit["distance"]), 6),
                        }
                        for index, hit in enumerate(hits)
                    ],
                }
            )

        manifest = json.loads(
            (settings.processed_root / "processing-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        expected_rows = manifest["embedding"]["records"]
        review = {
            "schema_version": 1,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "collection": settings.milvus_collection,
            "milvus_uri": settings.milvus_uri,
            "row_count": len(rows),
            "expected_row_count": expected_rows,
            "duplicate_content_hashes": duplicate_hashes,
            "invalid_rows": [row["id"] for row in invalid_rows],
            "top1_matches": top1_matches,
            "semantic_top1_matches": semantic_top1_matches,
            "attribute_recall_at_5": attribute_recall_at_5,
            "query_count": len(queries),
            "search_results": search_results,
            "checks": {
                "row_count_matches": len(rows) == expected_rows,
                "no_duplicate_hashes": not duplicate_hashes,
                "no_quarantined_rows": not invalid_rows,
                "all_query_dimensions_match": all(
                    item["query_vector_dimension"] == settings.embedding_dimension
                    for item in search_results
                ),
                "top1_accuracy": top1_matches / len(queries),
                "semantic_top1_accuracy": semantic_top1_matches / len(queries),
                "attribute_recall_at_5": attribute_recall_at_5 / len(queries),
            },
            "remaining_risks": [
                "Official benchmark tables remain image-derived and are quarantined until OCR/manual verification.",
                "voyage-code-3 is code-oriented; multilingual audit queries need a wider retrieval evaluation before production.",
                "Milvus currently contains only Fable 5, so cross-model contrast distributions are not yet available.",
                "Fallback behavior must always be filtered by surface and configuration during scoring.",
            ],
        }
        _write_json(settings.processed_root / "milvus-review.json", review)
        lines = [
            "# Claude Fable 5 Milvus 自审报告",
            "",
            f"- 集合：`{settings.milvus_collection}`",
            f"- 数据位置：`{settings.milvus_uri}`",
            f"- 记录：{len(rows)} / 预期 {expected_rows}",
            f"- 重复内容哈希：{len(duplicate_hashes)}",
            f"- 违规隔离记录：{len(invalid_rows)}",
            f"- 六组检索 Top-1 命中：{top1_matches}/{len(queries)}",
            f"- 六组语义 Top-1 命中：{semantic_top1_matches}/{len(queries)}",
            f"- 审计属性 Recall@5：{attribute_recall_at_5}/{len(queries)}",
            "",
            "## 检索结果",
            "",
        ]
        for item in search_results:
            top = item["hits"][0] if item["hits"] else None
            lines.extend(
                [
                    f"- 查询：{item['query']}",
                    f"  - 期望：`{item['expected_top_id']}`",
                    f"  - Top-1：`{top['id'] if top else 'NONE'}`",
                    f"  - 相似度：{top['distance'] if top else 'N/A'}",
                    f"  - 期望审计属性排名：{item['expected_attribute_rank'] or '未命中'}",
                ]
            )
        lines.extend(
            [
                "",
                "## 尚未入库",
                "",
                "- 带 Opus 4.8 fallback 的 Artificial Analysis 指标；",
                "- 未人工校验的官方 Benchmark 图片；",
                "- 官方营销评价和客户证言；",
                "- 日语二手 Benchmark 数字；",
                "- 价格、促销和数据保留等非模型行为信息。",
                "",
                "## 判断",
                "",
                "只有 Claim 与审计属性进入集合，原始网页章节没有直接 Embedding。数据库可用于下一阶段检索实验，但在加入对照模型和完成 Benchmark 图片校验前，不应作为最终模型真实性判决的唯一依据。",
            ]
        )
        (settings.processed_root / "milvus-review.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        print(json.dumps(review["checks"], ensure_ascii=False))
        if not all(
            [
                review["checks"]["row_count_matches"],
                review["checks"]["no_duplicate_hashes"],
                review["checks"]["no_quarantined_rows"],
                review["checks"]["all_query_dimensions_match"],
            ]
        ):
            return 2
    finally:
        store.close()
    return 0


def run_rag_test(args: argparse.Namespace) -> dict[str, Any]:
    settings = _settings(args)
    store = _store(settings)
    try:
        return run_fable5_rag_test(
            embedding=_embedding_client(settings),
            reranker=_reranker(settings),
            store=store,
            retrieval_top_k=settings.retrieval_top_k,
            rerank_top_k=settings.rerank_top_k,
            output_root=settings.processed_root,
        )
    finally:
        store.close()


def test_fable5_rag(args: argparse.Namespace) -> int:
    review = run_rag_test(args)
    print(json.dumps(review["metrics"], ensure_ascii=False, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TokenAudit knowledge pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, handler in (
        ("ingest-fable5", ingest_fable5),
        ("review-fable5", review_fable5),
        ("test-fable5-rag", test_fable5_rag),
        ("ingest-all-models", ingest_all_models),
        ("test-mixed-rag", test_mixed_rag),
    ):
        command = subparsers.add_parser(name)
        command.add_argument(
            "--env-file",
            action="append",
            required=True,
            help="May be repeated; later files override earlier files.",
        )
        if name in {"ingest-fable5", "ingest-all-models"}:
            command.add_argument("--rebuild", action="store_true")
        if name == "ingest-all-models":
            command.add_argument(
                "--skip-assets",
                action="store_true",
                help="Skip image download/OCR while retaining asset quarantine metadata.",
            )
            command.add_argument(
                "--reuse-processed",
                action="store_true",
                help="Reuse existing per-model processed files and only rebuild embeddings/Milvus.",
            )
        command.set_defaults(handler=handler)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
