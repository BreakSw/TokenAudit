from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .embedding import VoyageEmbeddingClient
from .milvus_store import KnowledgeMilvusStore
from .model_catalog import MODEL_BY_SLUG
from .rerank import VoyageRerankClient


FABLE_CASES = (
    {
        "name": "claude-fable-5-fallback",
        "model_id": "claude-fable-5",
        "query": (
            "How can an audit distinguish Claude Fable 5's official Opus fallback "
            "from an unauthorized relay model substitution?"
        ),
        "expected_attribute_id": "attr-fable5-fallback-disambiguation",
        "acceptable_ids": {
            "attr-fable5-fallback-disambiguation",
            "fable5-fallback-modes",
            "fable5-opus-fallback",
        },
    },
    {
        "name": "claude-fable-5-reasoning",
        "model_id": "claude-fable-5",
        "query": (
            "Can Claude Fable 5 disable thinking, and which effort parameter controls "
            "its reasoning depth?"
        ),
        "expected_attribute_id": "attr-fable5-adaptive-thinking",
        "acceptable_ids": {
            "attr-fable5-adaptive-thinking",
            "fable5-adaptive-thinking",
        },
    },
    {
        "name": "claude-fable-5-tools",
        "model_id": "claude-fable-5",
        "query": "Which complex tool and agent capabilities distinguish Claude Fable 5?",
        "expected_attribute_id": "attr-fable5-tools",
        "acceptable_ids": {
            "attr-fable5-tools",
            "fable5-supported-features",
        },
    },
)


PREFERRED_TEST_CATEGORIES = (
    "reasoning_behavior",
    "context_output",
    "architecture",
    "api_behavior",
    "modalities",
    "tools_agents",
    "performance",
    "pricing",
    "model_identity",
    "safety_behavior",
)


def build_mixed_test_cases(
    records: list[dict[str, Any]],
    *,
    cases_per_model: int = 2,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = [dict(case) for case in FABLE_CASES]
    attributes_by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("record_type") == "attribute":
            attributes_by_model[record["model_id"]].append(record)

    preference = {
        category: index for index, category in enumerate(PREFERRED_TEST_CATEGORIES)
    }
    for model_id, attributes in sorted(attributes_by_model.items()):
        if model_id == "claude-fable-5":
            continue
        selected = sorted(
            attributes,
            key=lambda item: (
                preference.get(item.get("predicate", ""), 999),
                item["id"],
            ),
        )[:cases_per_model]
        for attribute in selected:
            source_claim_ids = set(attribute.get("source_claim_ids", []))
            evidence_chunk_ids = set(attribute.get("evidence_chunk_ids", []))
            cases.append(
                {
                    "name": f"{model_id}-{attribute.get('predicate', 'attribute')}",
                    "model_id": model_id,
                    "query": attribute["audit_question"],
                    "expected_attribute_id": attribute["id"],
                    "acceptable_ids": {
                        attribute["id"],
                        *source_claim_ids,
                        *evidence_chunk_ids,
                    },
                }
            )
    return cases


def _rank(ids: list[str], expected: set[str]) -> int | None:
    for index, record_id in enumerate(ids, start=1):
        if record_id in expected:
            return index
    return None


def _ndcg(ids: list[str], expected: set[str]) -> float:
    relevant = sum(record_id in expected for record_id in ids)
    if not ids or not relevant:
        return 0.0
    dcg = sum(
        1 / math.log2(index + 1)
        for index, record_id in enumerate(ids, start=1)
        if record_id in expected
    )
    ideal_count = min(len(expected), len(ids))
    ideal = sum(1 / math.log2(index + 1) for index in range(1, ideal_count + 1))
    return dcg / ideal if ideal else 0.0


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def run_mixed_rag_test(
    *,
    embedding: VoyageEmbeddingClient,
    reranker: VoyageRerankClient,
    store: KnowledgeMilvusStore,
    records: list[dict[str, Any]],
    model_coverage: list[dict[str, Any]],
    retrieval_top_k: int,
    rerank_top_k: int,
    output_root: Path,
) -> dict[str, Any]:
    test_cases = build_mixed_test_cases(records)
    store.load_collection()
    query_vectors = embedding.embed_queries([case["query"] for case in test_cases])
    results: list[dict[str, Any]] = []

    for case, query_vector in zip(test_cases, query_vectors, strict=True):
        vector_hits = store.search(query_vector, limit=retrieval_top_k)
        rerank_results = reranker.rerank(
            case["query"],
            [hit["entity"]["text"] for hit in vector_hits],
            top_k=rerank_top_k,
        )
        vector_rows = [
            {
                "rank": index,
                "id": hit["entity"]["id"],
                "model_id": hit["entity"]["model_id"],
                "record_type": hit["entity"]["record_type"],
                "source_id": hit["entity"]["source_id"],
                "score": round(float(hit["distance"]), 6),
            }
            for index, hit in enumerate(vector_hits, start=1)
        ]
        reranked_rows: list[dict[str, Any]] = []
        for index, rerank_result in enumerate(rerank_results, start=1):
            original = vector_hits[rerank_result["index"]]
            entity = original["entity"]
            reranked_rows.append(
                {
                    "rank": index,
                    "id": entity["id"],
                    "model_id": entity["model_id"],
                    "record_type": entity["record_type"],
                    "source_id": entity["source_id"],
                    "vector_rank": rerank_result["index"] + 1,
                    "vector_score": round(float(original["distance"]), 6),
                    "rerank_score": round(rerank_result["relevance_score"], 6),
                }
            )

        expected = set(case["acceptable_ids"])
        vector_ids = [row["id"] for row in vector_rows]
        rerank_ids = [row["id"] for row in reranked_rows]
        vector_semantic_rank = _rank(vector_ids, expected)
        rerank_semantic_rank = _rank(rerank_ids, expected)
        expected_attribute_rank = _rank(
            rerank_ids, {case["expected_attribute_id"]}
        )
        results.append(
            {
                "name": case["name"],
                "model_id": case["model_id"],
                "query": case["query"],
                "expected_attribute_id": case["expected_attribute_id"],
                "acceptable_ids": sorted(expected),
                "query_vector_dimension": len(query_vector),
                "vector_hits": vector_rows,
                "reranked_hits": reranked_rows,
                "vector_semantic_rank": vector_semantic_rank,
                "rerank_semantic_rank": rerank_semantic_rank,
                "expected_attribute_rank": expected_attribute_rank,
                "vector_model_rank": next(
                    (
                        row["rank"]
                        for row in vector_rows
                        if row["model_id"] == case["model_id"]
                    ),
                    None,
                ),
                "rerank_model_rank": next(
                    (
                        row["rank"]
                        for row in reranked_rows
                        if row["model_id"] == case["model_id"]
                    ),
                    None,
                ),
                "vector_ndcg": _ndcg(vector_ids, expected),
                "rerank_ndcg": _ndcg(rerank_ids, expected),
            }
        )

    def metrics_for(items: list[dict[str, Any]]) -> dict[str, float | int]:
        count = len(items)
        return {
            "cases": count,
            "vector_top1_accuracy": _mean(
                [float(item["vector_semantic_rank"] == 1) for item in items]
            ),
            f"vector_recall_at_{retrieval_top_k}": _mean(
                [float(item["vector_semantic_rank"] is not None) for item in items]
            ),
            f"vector_mrr_at_{retrieval_top_k}": _mean(
                [
                    1 / item["vector_semantic_rank"]
                    if item["vector_semantic_rank"]
                    else 0.0
                    for item in items
                ]
            ),
            f"vector_ndcg_at_{retrieval_top_k}": _mean(
                [item["vector_ndcg"] for item in items]
            ),
            "vector_model_top1_accuracy": _mean(
                [float(item["vector_model_rank"] == 1) for item in items]
            ),
            f"vector_model_recall_at_{retrieval_top_k}": _mean(
                [float(item["vector_model_rank"] is not None) for item in items]
            ),
            "rerank_top1_accuracy": _mean(
                [float(item["rerank_semantic_rank"] == 1) for item in items]
            ),
            f"rerank_recall_at_{rerank_top_k}": _mean(
                [float(item["rerank_semantic_rank"] is not None) for item in items]
            ),
            f"rerank_mrr_at_{rerank_top_k}": _mean(
                [
                    1 / item["rerank_semantic_rank"]
                    if item["rerank_semantic_rank"]
                    else 0.0
                    for item in items
                ]
            ),
            f"rerank_ndcg_at_{rerank_top_k}": _mean(
                [item["rerank_ndcg"] for item in items]
            ),
            "rerank_model_top1_accuracy": _mean(
                [float(item["rerank_model_rank"] == 1) for item in items]
            ),
            f"attribute_exact_recall_at_{rerank_top_k}": _mean(
                [float(item["expected_attribute_rank"] is not None) for item in items]
            ),
        }

    per_model = {
        model_id: metrics_for(
            [item for item in results if item["model_id"] == model_id]
        )
        for model_id in sorted({item["model_id"] for item in results})
    }
    report = {
        "schema_version": 1,
        "tested_at": datetime.now(timezone.utc).isoformat(),
        "collection": store.collection,
        "retrieval_top_k": retrieval_top_k,
        "rerank_top_k": rerank_top_k,
        "database_records": len(records),
        "test_cases": len(results),
        "coverage": model_coverage,
        "metrics": metrics_for(results),
        "per_model_metrics": per_model,
        "cases": results,
        "limitations": [
            "The evaluation set is deterministic and derived from admitted source-backed attributes; it is a smoke test, not an independent benchmark.",
            "Models with HOLD or mismatched source bodies are excluded from scored queries rather than assigned fabricated Ground Truth.",
            "A successful retrieval result validates this corpus and query set, not the authenticity of any relay model by itself.",
        ],
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "mixed-rag-test-results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "mixed-rag-test.log").write_text(
        _render_log(report), encoding="utf-8"
    )
    (output_root / "mixed-rag-report.md").write_text(
        _render_markdown(report), encoding="utf-8"
    )
    return report


def _render_log(report: dict[str, Any]) -> str:
    lines = [
        f"tested_at={report['tested_at']}",
        f"collection={report['collection']}",
        f"database_records={report['database_records']}",
        f"test_cases={report['test_cases']}",
        f"retrieval_top_k={report['retrieval_top_k']}",
        f"rerank_top_k={report['rerank_top_k']}",
    ]
    for name, value in report["metrics"].items():
        rendered = f"{value:.6f}" if isinstance(value, float) else str(value)
        lines.append(f"metric.{name}={rendered}")
    for case in report["cases"]:
        lines.extend(
            [
                f"case={case['name']}",
                f"vector_semantic_rank={case['vector_semantic_rank'] or 'MISS'}",
                f"rerank_semantic_rank={case['rerank_semantic_rank'] or 'MISS'}",
                f"expected_attribute_rank={case['expected_attribute_rank'] or 'MISS'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    retrieval_k = report["retrieval_top_k"]
    rerank_k = report["rerank_top_k"]
    lines = [
        "# 多模型混合 RAG 检索评测报告",
        "",
        f"- Milvus 集合：`{report['collection']}`",
        f"- 入库记录：{report['database_records']}",
        f"- 测试问题：{report['test_cases']}",
        f"- 向量初检 Top-K：{retrieval_k}",
        f"- Voyage Rerank 保留：{rerank_k}",
        "",
        "## 总体指标",
        "",
        f"- Vector Top-1 Accuracy：{metrics['vector_top1_accuracy']:.1%}",
        f"- Vector Recall@{retrieval_k}：{metrics[f'vector_recall_at_{retrieval_k}']:.1%}",
        f"- Vector MRR@{retrieval_k}：{metrics[f'vector_mrr_at_{retrieval_k}']:.4f}",
        f"- Vector nDCG@{retrieval_k}：{metrics[f'vector_ndcg_at_{retrieval_k}']:.4f}",
        f"- Vector 模型 Top-1 Accuracy：{metrics['vector_model_top1_accuracy']:.1%}",
        f"- Rerank Top-1 Accuracy：{metrics['rerank_top1_accuracy']:.1%}",
        f"- Rerank Recall@{rerank_k}：{metrics[f'rerank_recall_at_{rerank_k}']:.1%}",
        f"- Rerank MRR@{rerank_k}：{metrics[f'rerank_mrr_at_{rerank_k}']:.4f}",
        f"- Rerank nDCG@{rerank_k}：{metrics[f'rerank_ndcg_at_{rerank_k}']:.4f}",
        f"- Rerank 模型 Top-1 Accuracy：{metrics['rerank_model_top1_accuracy']:.1%}",
        f"- 精确审计属性 Recall@{rerank_k}：{metrics[f'attribute_exact_recall_at_{rerank_k}']:.1%}",
        "",
        "## 数据覆盖",
        "",
        "| 模型 | 来源状态 | 入库记录 | Claim | 属性 | 覆盖缺口 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in report["coverage"]:
        gaps = "；".join(item.get("coverage_gaps", [])) or "无硬性缺口"
        lines.append(
            f"| {item['model_id']} | {item['source_review_status']} | "
            f"{item['records']} | {item['claims']} | {item['attributes']} | {gaps} |"
        )
    lines.extend(
        [
            "",
            "## 分模型指标",
            "",
            "| 模型 | 问题数 | Vector Top-1 | Vector Recall | Rerank Top-1 | Rerank Recall |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for model_id, model_metrics in report["per_model_metrics"].items():
        lines.append(
            f"| {model_id} | {model_metrics['cases']} | "
            f"{model_metrics['vector_top1_accuracy']:.1%} | "
            f"{model_metrics[f'vector_recall_at_{retrieval_k}']:.1%} | "
            f"{model_metrics['rerank_top1_accuracy']:.1%} | "
            f"{model_metrics[f'rerank_recall_at_{rerank_k}']:.1%} |"
        )
    lines.extend(["", "## 逐题结果", ""])
    for case in report["cases"]:
        vector_top = case["vector_hits"][0] if case["vector_hits"] else None
        rerank_top = case["reranked_hits"][0] if case["reranked_hits"] else None
        lines.extend(
            [
                f"### {case['name']}",
                "",
                f"- 查询：{case['query']}",
                f"- Vector Top-1：`{vector_top['id'] if vector_top else 'NONE'}`",
                f"- Rerank Top-1：`{rerank_top['id'] if rerank_top else 'NONE'}`",
                f"- 目标属性排名：{case['expected_attribute_rank'] or '未进入结果'}",
                "",
            ]
        )
    lines.extend(
        [
            "## 局限",
            "",
            *[f"- {item}" for item in report["limitations"]],
        ]
    )
    return "\n".join(lines) + "\n"
