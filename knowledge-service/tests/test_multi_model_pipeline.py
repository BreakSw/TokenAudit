from __future__ import annotations

from tokenaudit_knowledge.model_catalog import (
    get_model_spec,
    resolve_knowledge_baseline,
)
from tokenaudit_knowledge.multi_model_pipeline import MultiModelAuditProcessor


def _chunk(text: str, *, level: str = "P0") -> dict[str, object]:
    return {
        "id": "chunk-test",
        "text": text,
        "source_id": "01-official",
        "source_level": level,
        "source_url": "https://example.test/model",
        "captured_at": "2026-08-24T00:00:00Z",
    }


def test_extract_claims_requires_target_model_in_page_body() -> None:
    processor = object.__new__(MultiModelAuditProcessor)
    spec = get_model_spec("qwen3-max")
    claims, coverage = processor._extract_claims(
        spec,
        [_chunk("Qwen3 supports hybrid thinking and tool calling.")],
    )

    assert claims == []
    assert coverage["explicit_model_chunks"] == 0
    assert "No captured page body explicitly names the target model" in coverage[
        "coverage_gaps"
    ][0]


def test_extract_claims_admits_source_backed_p0_reasoning() -> None:
    processor = object.__new__(MultiModelAuditProcessor)
    spec = get_model_spec("glm-5.2")
    claims, _ = processor._extract_claims(
        spec,
        [
            _chunk(
                "GLM-5.2 always has reasoning enabled. The reasoning_effort "
                "parameter supports low, high, and max; disabling thinking makes "
                "the request fail."
            )
        ],
    )

    reasoning = next(
        claim for claim in claims if claim["claim_type"] == "reasoning_behavior"
    )
    assert reasoning["eligible_for_ground_truth"] is True
    assert reasoning["evidence_chunk_id"] == "chunk-test"


def test_glm_53_uses_explicit_glm_52_proxy_baseline() -> None:
    resolution = resolve_knowledge_baseline("GLM-5.3")

    assert resolution.declared_model_id == "glm-5.3"
    assert resolution.knowledge_model_id == "glm-5.2"
    assert resolution.baseline_kind == "proxy"
    assert "GLM-5.2" in (resolution.baseline_reason or "")
    assert get_model_spec("glm-5.3").slug == "glm-5.2"


def test_extract_claims_quarantines_p2_only_evidence() -> None:
    processor = object.__new__(MultiModelAuditProcessor)
    spec = get_model_spec("deepseek-v4-pro")
    claims, _ = processor._extract_claims(
        spec,
        [
            _chunk(
                "DeepSeek-V4-Pro supports a one million-token context window and "
                "a maximum output limit.",
                level="P2",
            )
        ],
    )

    assert claims
    assert all(not claim["eligible_for_ground_truth"] for claim in claims)
    assert all("P0/P1" in claim["quarantine_reason"] for claim in claims)
