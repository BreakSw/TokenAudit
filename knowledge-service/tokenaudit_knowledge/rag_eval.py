from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .embedding import VoyageEmbeddingClient
from .milvus_store import KnowledgeMilvusStore
from .rerank import VoyageRerankClient


FABLE5_TEST_CASES = [
    {
        "name": "fallback_disambiguation",
        "query": "如何区分 Fable 5 官方回退到 Opus 4.8 与中转站偷偷替换模型？",
        "expected_attribute_id": "attr-fable5-fallback-disambiguation",
        "acceptable_ids": {
            "attr-fable5-fallback-disambiguation",
            "fable5-fallback-modes",
            "fable5-opus-fallback",
        },
    },
    {
        "name": "adaptive_thinking",
        "query": "Claude Fable 5 能不能关闭 thinking，应该用什么参数控制推理深度？",
        "expected_attribute_id": "attr-fable5-adaptive-thinking",
        "acceptable_ids": {
            "attr-fable5-adaptive-thinking",
            "fable5-adaptive-thinking",
        },
    },
    {
        "name": "tool_capabilities",
        "query": "Fable 5 有哪些能够区分普通模型的复杂工具与 Agent 能力？",
        "expected_attribute_id": "attr-fable5-tools",
        "acceptable_ids": {
            "attr-fable5-tools",
            "fable5-supported-features",
        },
    },
]


def run_fable5_rag_test(
    *,
    embedding: VoyageEmbeddingClient,
    reranker: VoyageRerankClient,
    store: KnowledgeMilvusStore,
    retrieval_top_k: int,
    rerank_top_k: int,
    output_root: Path,
) -> dict[str, Any]:
    store.load_collection()
    query_vectors = embedding.embed_queries(
        [case["query"] for case in FABLE5_TEST_CASES]
    )
    cases: list[dict[str, Any]] = []

    for case, query_vector in zip(FABLE5_TEST_CASES, query_vectors, strict=True):
        vector_hits = store.search(
            query_vector,
            limit=retrieval_top_k,
            model_id="claude-fable-5",
        )
        rerank_results = reranker.rerank(
            case["query"],
            [hit["entity"]["text"] for hit in vector_hits],
            top_k=rerank_top_k,
        )
        reranked_hits = []
        for rank, rerank_result in enumerate(rerank_results, start=1):
            original = vector_hits[rerank_result["index"]]
            reranked_hits.append(
                {
                    "rank": rank,
                    "id": original["entity"]["id"],
                    "record_type": original["entity"]["record_type"],
                    "source_id": original["entity"]["source_id"],
                    "vector_rank": rerank_result["index"] + 1,
                    "vector_score": round(float(original["distance"]), 6),
                    "rerank_score": round(rerank_result["relevance_score"], 6),
                }
            )

        vector_ids = [hit["entity"]["id"] for hit in vector_hits]
        reranked_ids = [hit["id"] for hit in reranked_hits]
        cases.append(
            {
                "name": case["name"],
                "query": case["query"],
                "query_vector_dimension": len(query_vector),
                "query_vector_norm": round(
                    math.sqrt(sum(value * value for value in query_vector)), 6
                ),
                "expected_attribute_id": case["expected_attribute_id"],
                "acceptable_ids": sorted(case["acceptable_ids"]),
                "vector_top_ids": vector_ids,
                "vector_semantic_top1": bool(
                    vector_ids and vector_ids[0] in case["acceptable_ids"]
                ),
                "reranked_hits": reranked_hits,
                "rerank_semantic_top1": bool(
                    reranked_ids and reranked_ids[0] in case["acceptable_ids"]
                ),
                "expected_attribute_rank": (
                    reranked_ids.index(case["expected_attribute_id"]) + 1
                    if case["expected_attribute_id"] in reranked_ids
                    else None
                ),
            }
        )

    count = len(cases)
    review = {
        "schema_version": 1,
        "tested_at": datetime.now(timezone.utc).isoformat(),
        "model_id": "claude-fable-5",
        "retrieval_top_k": retrieval_top_k,
        "rerank_top_k": rerank_top_k,
        "test_cases": count,
        "metrics": {
            "vector_semantic_top1_accuracy": sum(
                case["vector_semantic_top1"] for case in cases
            )
            / count,
            "rerank_semantic_top1_accuracy": sum(
                case["rerank_semantic_top1"] for case in cases
            )
            / count,
            "attribute_recall_at_rerank_k": sum(
                case["expected_attribute_rank"] is not None for case in cases
            )
            / count,
            "attribute_mrr": sum(
                1 / case["expected_attribute_rank"]
                if case["expected_attribute_rank"]
                else 0
                for case in cases
            )
            / count,
        },
        "cases": cases,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "rag-test-results.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "rag-test.log").write_text(
        _render_log(review),
        encoding="utf-8",
    )
    (output_root / "rag-test-report.md").write_text(
        _render_markdown(review),
        encoding="utf-8",
    )
    return review


def _render_log(review: dict[str, Any]) -> str:
    lines = [
        f"tested_at={review['tested_at']}",
        f"model_id={review['model_id']}",
        f"retrieval_top_k={review['retrieval_top_k']}",
        f"rerank_top_k={review['rerank_top_k']}",
    ]
    for case in review["cases"]:
        top = case["reranked_hits"][0] if case["reranked_hits"] else None
        lines.extend(
            [
                f"case={case['name']}",
                f"query={case['query']}",
                f"vector_top1={case['vector_top_ids'][0] if case['vector_top_ids'] else 'NONE'}",
                f"rerank_top1={top['id'] if top else 'NONE'}",
                f"rerank_top1_score={top['rerank_score'] if top else 'N/A'}",
                f"expected_attribute_rank={case['expected_attribute_rank'] or 'MISS'}",
            ]
        )
    for name, value in review["metrics"].items():
        lines.append(f"metric.{name}={value:.6f}")
    return "\n".join(lines) + "\n"


def _render_markdown(review: dict[str, Any]) -> str:
    metrics = review["metrics"]
    lines = [
        "# Claude Fable 5 RAG 效果测试",
        "",
        f"- 初检 Top-K：{review['retrieval_top_k']}",
        f"- Rerank 保留：{review['rerank_top_k']}",
        f"- 向量语义 Top-1：{metrics['vector_semantic_top1_accuracy']:.1%}",
        f"- Rerank 语义 Top-1：{metrics['rerank_semantic_top1_accuracy']:.1%}",
        f"- 审计属性 Recall@{review['rerank_top_k']}：{metrics['attribute_recall_at_rerank_k']:.1%}",
        f"- 审计属性 MRR：{metrics['attribute_mrr']:.4f}",
        "",
        "## 用例",
        "",
    ]
    for case in review["cases"]:
        top = case["reranked_hits"][0] if case["reranked_hits"] else None
        lines.extend(
            [
                f"### {case['name']}",
                "",
                f"- 查询：{case['query']}",
                f"- 向量 Top-1：`{case['vector_top_ids'][0] if case['vector_top_ids'] else 'NONE'}`",
                f"- Rerank Top-1：`{top['id'] if top else 'NONE'}`",
                f"- 目标审计属性排名：{case['expected_attribute_rank'] or '未进入结果'}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"
