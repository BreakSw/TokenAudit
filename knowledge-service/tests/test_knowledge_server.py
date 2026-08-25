from tokenaudit_knowledge.server import KnowledgeApplication


class _FakeRetriever:
    def retrieve(self, *, model_id, query):
        return {"declared_model_id": model_id, "query": query}


def test_application_requires_model_and_query():
    application = KnowledgeApplication(_FakeRetriever())
    try:
        application.retrieve({"model_id": "deepseek-v4-pro"})
    except ValueError as exc:
        assert "required" in str(exc)
    else:
        raise AssertionError("missing query should fail")


def test_application_delegates_retrieval():
    application = KnowledgeApplication(_FakeRetriever())
    result = application.retrieve({"model_id": "deepseek-v4-pro", "query": "tool behavior"})
    assert result["declared_model_id"] == "deepseek-v4-pro"
