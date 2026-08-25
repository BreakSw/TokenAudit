from tokenaudit_knowledge.model_catalog import resolve_knowledge_baseline


def test_openrouter_model_prefix_is_normalized():
    result = resolve_knowledge_baseline("deepseek/deepseek-v4-pro")
    assert result.knowledge_model_id == "deepseek-v4-pro"
    assert result.spec_model_id == "deepseek-v4-pro"
    assert result.behavior_model_id == "deepseek-v4-pro"
    assert result.baseline_kind == "exact"


def test_glm_53_uses_visible_proxy_baseline():
    result = resolve_knowledge_baseline("provider/glm-5.3")
    assert result.knowledge_model_id == "glm-5.2"
    assert result.spec_model_id == "glm-5.3"
    assert result.behavior_model_id == "glm-5.2"
    assert result.baseline_kind == "proxy"
    assert result.baseline_reason
