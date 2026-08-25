from tokenaudit_knowledge.hybrid_retriever import HybridAuditRetriever
from tokenaudit_knowledge.model_catalog import resolve_knowledge_baseline


def test_declared_openrouter_id_resolves_to_behavior_collection_model():
    assert resolve_knowledge_baseline("deepseek/deepseek-v4-pro").knowledge_model_id == "deepseek-v4-pro"


def test_rerank_candidates_fit_free_tier_character_budget():
    captured = {}

    class FakeReranker:
        def rerank(self, query, documents, *, top_k):
            captured["documents"] = documents
            return [{"index": 0, "relevance_score": 0.9}]

    retriever = object.__new__(HybridAuditRetriever)
    retriever.reranker = FakeReranker()
    hits = [
        {"id": str(index), "entity": {"text": "x" * 8192, "payload_json": "{}"}}
        for index in range(20)
    ]

    result = retriever._rerank("query", hits, top_k=8)

    assert len(result) == 1
    assert sum(len(document) for document in captured["documents"]) <= 8_000
    assert max(len(document) for document in captured["documents"]) == 400
