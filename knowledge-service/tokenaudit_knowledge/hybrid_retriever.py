from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from pymilvus import MilvusClient

from .behavior_store import BehaviorMilvusStore
from .config import KnowledgeSettings
from .embedding import VoyageEmbeddingClient
from .milvus_store import KnowledgeMilvusStore
from .model_catalog import resolve_knowledge_baseline
from .rerank import VoyageRerankClient


class HybridAuditRetriever:
    """Retrieve hard specification evidence and soft behavior evidence separately."""

    # Voyage's unbilled tier is capped at 10K TPM. Keep each rerank request
    # below that ceiling even when the candidate set contains multilingual text.
    RERANK_BATCH_CHARACTER_BUDGET = 8_000
    RERANK_DOCUMENT_CHARACTER_CAP = 1_200

    def __init__(self, settings: KnowledgeSettings) -> None:
        self.settings = settings
        self.embedder = VoyageEmbeddingClient(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
            timeout_seconds=settings.embedding_timeout_seconds,
        )
        self.reranker = VoyageRerankClient(
            base_url=settings.rerank_base_url,
            api_key=settings.rerank_api_key,
            model=settings.rerank_model,
            timeout_seconds=settings.rerank_timeout_seconds,
        )
        spec_collection = self._resolve_spec_collection(settings)
        self.spec_store = KnowledgeMilvusStore(
            uri=settings.milvus_uri,
            token=settings.milvus_token,
            database=settings.milvus_database,
            collection=spec_collection,
            dimension=settings.embedding_dimension,
            metric_type=settings.milvus_metric_type,
        )
        self.behavior_store = BehaviorMilvusStore(
            uri=settings.milvus_uri,
            token=settings.milvus_token,
            database=settings.milvus_database,
            collection=settings.behavior_collection,
            dimension=settings.embedding_dimension,
            metric_type=settings.milvus_metric_type,
        )
        self.spec_store.load_collection()
        self.behavior_store.load_collection()

    @staticmethod
    def load(env_files: Iterable[str | Path]) -> "HybridAuditRetriever":
        return HybridAuditRetriever(KnowledgeSettings.load(env_files))

    @staticmethod
    def _resolve_spec_collection(settings: KnowledgeSettings) -> str:
        client = MilvusClient(uri=settings.milvus_uri)
        try:
            available = set(client.list_collections())
        finally:
            client.close()
        for candidate in (
            settings.milvus_collection,
            "tokenaudit_knowledge_v4",
            "tokenaudit_knowledge_v3",
            "tokenaudit_knowledge_v2",
        ):
            if candidate in available:
                return candidate
        raise ValueError("No TokenAudit specification collection exists in Milvus.")

    def close(self) -> None:
        self.spec_store.close()
        self.behavior_store.close()

    def retrieve(self, *, model_id: str, query: str) -> dict[str, Any]:
        baseline = resolve_knowledge_baseline(model_id)
        query_vector = self.embedder.embed_query(query)
        spec_hits = self.spec_store.search(
            query_vector,
            limit=self.settings.retrieval_top_k,
            model_id=model_id,
        )
        claimed_hits = self.behavior_store.search(
            query_vector,
            limit=self.settings.behavior_retrieval_top_k,
            model_id=model_id,
            include_persona_contaminated=False,
        )
        contrast_hits = self.behavior_store.search(
            query_vector,
            limit=self.settings.behavior_retrieval_top_k,
            exclude_model_id=model_id,
            include_persona_contaminated=False,
        )
        return {
            "declared_model_id": baseline.declared_model_id,
            "knowledge_model_id": baseline.knowledge_model_id,
            "spec_model_id": baseline.spec_model_id,
            "behavior_model_id": baseline.behavior_model_id,
            "baseline_kind": baseline.baseline_kind,
            "baseline_reason": baseline.baseline_reason,
            "collections": {
                "spec": self.spec_store.collection,
                "behavior": self.behavior_store.collection,
            },
            "spec_evidence": self._rerank(query, spec_hits, self.settings.rerank_top_k),
            "claimed_behavior": self._rerank(query, claimed_hits, self.settings.behavior_rerank_top_k),
            "contrast_behavior": self._rerank(query, contrast_hits, self.settings.behavior_rerank_top_k),
        }

    def _rerank(self, query: str, hits: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not hits:
            return []
        per_document_limit = min(
            self.RERANK_DOCUMENT_CHARACTER_CAP,
            max(200, self.RERANK_BATCH_CHARACTER_BUDGET // len(hits)),
        )
        reranked = self.reranker.rerank(
            query,
            [
                str(hit.get("entity", {}).get("text") or "")[:per_document_limit]
                for hit in hits
            ],
            top_k=top_k,
        )
        output: list[dict[str, Any]] = []
        for rank, result in enumerate(reranked, start=1):
            hit = hits[result["index"]]
            entity = dict(hit.get("entity") or {})
            payload_text = entity.pop("payload_json", "")
            try:
                payload = json.loads(payload_text) if payload_text else {}
            except Exception:
                payload = {}
            output.append(
                {
                    **entity,
                    "id": hit.get("id") or entity.get("id"),
                    "vector_distance": float(hit.get("distance", 0.0)),
                    "rerank_score": float(result["relevance_score"]),
                    "rerank_rank": rank,
                    "payload": payload,
                }
            )
        return output


def compact_evidence(bundle: dict[str, Any], *, text_limit: int = 900) -> dict[str, Any]:
    """Bound the evidence passed into an audit-model prompt."""

    result = {key: value for key, value in bundle.items() if key not in {"spec_evidence", "claimed_behavior", "contrast_behavior"}}
    for key in ("spec_evidence", "claimed_behavior", "contrast_behavior"):
        rows = []
        for item in bundle.get(key, []):
            rows.append(
                {
                    "id": item.get("id"),
                    "model_id": item.get("model_id"),
                    "source_id": item.get("source_id"),
                    "source_level": item.get("source_level"),
                    "claim_type": item.get("claim_type"),
                    "record_type": item.get("record_type"),
                    "sample_kind": item.get("sample_kind"),
                    "task_type": item.get("task_type"),
                    "outcome": item.get("outcome"),
                    "confidence": item.get("confidence"),
                    "observed_only": item.get("observed_only"),
                    "text": str(item.get("text") or "")[:text_limit],
                    "rerank_score": item.get("rerank_score"),
                }
            )
        result[key] = rows
    return result
