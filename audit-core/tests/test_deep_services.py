import json
import pytest

from audit_core.agents.orchestrator_agent import OrchestratorInput
from audit_core.config import AuditConfig
from audit_core.deep.orchestrator import DeepAuditSettings, build_deep_report_markdown
from audit_core.deep.agents import (
    AuditJudgeAgent,
    GroundTruthCuratorAgent,
    ProbeDesignerAgent,
    _normalize_consistency_output,
)
from audit_core.deep.llm import AgentOutputError
from unittest.mock import patch

from audit_core.deep.services import (
    TargetTransportError,
    ensure_target_transport_integrity,
    execute_variants,
    fuse_scores,
    verify_objective_checks,
)


def test_deep_settings_clamps_rounds_and_keeps_three_variants():
    settings = DeepAuditSettings(rounds=99, variants_per_question=7).normalized()
    assert settings.rounds == 5
    assert settings.variants_per_question == 3
    assert settings.target_concurrency == 1


def test_objective_variants_are_collapsed_to_one_group_score():
    groups = [
        {
            "probe_group_id": "r1-p1",
            "objective_checks": [{"type": "json_keys", "values": ["answer"]}],
        }
    ]
    responses = [
        {"probe_group_id": "r1-p1", "variant_id": "v1", "ok": True, "response_text": '{"answer": 1}'},
        {"probe_group_id": "r1-p1", "variant_id": "v2", "ok": True, "response_text": '{"answer": 2}'},
        {"probe_group_id": "r1-p1", "variant_id": "v3", "ok": False, "response_text": ""},
    ]
    result = verify_objective_checks(groups, responses)
    assert len(result["groups"]) == 1
    assert result["score"] == 100.0
    assert result["groups"][0]["scored_variants"] == 2
    assert result["groups"][0]["unscorable_variants"] == 1


def test_score_fusion_is_deterministic():
    rounds = [
        {
            "objective": {"score": 80},
            "audit_judgement": {"semantic_score": 90, "ground_truth_alignment_score": 70},
            "behavior_judgement": {"behavior_score": 60},
            "consistency_judgement": {"consistency_score": 100},
            "responses": [{"ok": True}],
        }
    ]
    result = fuse_scores(rounds, coverage=1.0)
    assert result["total_score"] == 79.5
    assert result["band"] == "partially_consistent"


def test_target_call_retries_empty_reasoning_only_response_with_larger_budget():
    empty_reasoning = {
        "ok": True,
        "status_code": 200,
        "elapsed_ms": 10,
        "response": {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "", "reasoning_content": "thinking"},
                }
            ]
        },
    }
    final_response = {
        "ok": True,
        "status_code": 200,
        "elapsed_ms": 20,
        "response": {
            "choices": [
                {"finish_reason": "stop", "message": {"content": "final answer"}}
            ]
        },
    }
    groups = [
        {
            "probe_group_id": "r1-p1",
            "max_tokens": 800,
            "variants": [
                {"variant_id": "r1-p1-v1", "variant_type": "paraphrase", "prompt": "solve"}
            ],
        }
    ]

    with patch(
        "audit_core.deep.services.token_chat",
        side_effect=[empty_reasoning, final_response],
    ) as mocked:
        responses = execute_variants(
            base_url="https://relay.example/v1",
            token="secret",
            model="reasoning-model",
            round_index=1,
            groups=groups,
            timeout_s=30,
            concurrency=1,
        )

    assert mocked.call_count == 2
    assert mocked.call_args_list[1].kwargs["max_tokens"] == 4800
    assert responses[0]["ok"] is True
    assert responses[0]["response_text"] == "final answer"
    assert responses[0]["retry_count"] == 1


def test_probe_designer_gives_target_the_full_output_budget_below_100k():
    for proposed in (800, 20000, 100000):
        agent_output = {
            "probes": [
                {
                    "dimension": "coding",
                    "prompt": "Implement and explain a parser.",
                    "why_discriminative": "Tests implementation style.",
                    "invariants": ["same task"],
                    "reference_facts": ["reference"],
                    "rubric": ["complete"],
                    "objective_checks": [{"type": "min_length", "value": 10}],
                    "max_tokens": proposed,
                }
            ]
        }
        with patch("audit_core.deep.agents.call_json_agent", return_value=agent_output):
            probes = ProbeDesignerAgent().run(
                config=None,
                ground_truth={},
                round_index=1,
                question_count=1,
                previous_rounds=[],
                previous_prompts=[],
            )

        assert probes[0]["max_tokens"] == 99_999


def test_target_call_reduces_budget_after_402_affordability_error():
    insufficient_credit = {
        "ok": False,
        "status_code": 402,
        "elapsed_ms": 8,
        "response": {"error": {"message": "This request can only afford 13,867 tokens"}},
    }
    final_response = {
        "ok": True,
        "status_code": 200,
        "elapsed_ms": 12,
        "response": {"choices": [{"finish_reason": "stop", "message": {"content": "final answer"}}]},
    }
    groups = [
        {
            "probe_group_id": "r1-p1",
            "max_tokens": 32000,
            "variants": [{"variant_id": "r1-p1-v1", "variant_type": "boundary", "prompt": "solve"}],
        }
    ]

    with (
        patch("audit_core.deep.services.token_chat", side_effect=[insufficient_credit, final_response]) as mocked,
        patch("audit_core.deep.services.log_event") as event,
    ):
        responses = execute_variants(
            base_url="https://relay.example/v1",
            token="secret",
            model="reasoning-model",
            round_index=1,
            groups=groups,
            timeout_s=30,
            concurrency=1,
        )

    assert mocked.call_args_list[0].kwargs["max_tokens"] == 32000
    assert mocked.call_args_list[1].kwargs["max_tokens"] == 12480
    assert responses[0]["ok"] is True
    assert responses[0]["retry_count"] == 1
    assert responses[0]["requested_max_tokens"] == 32000
    assert responses[0]["used_max_tokens"] == 12480
    retry = next(call for call in event.call_args_list if call.args[0] == "deep_target_call_retry")
    assert retry.args[1]["reason"] == "insufficient_credits_reduce_budget"
    assert retry.args[1]["affordable_max_tokens"] == 13867


def test_target_call_never_requests_exactly_100k():
    successful = {
        "ok": True,
        "status_code": 200,
        "elapsed_ms": 5,
        "response": {"choices": [{"finish_reason": "stop", "message": {"content": "ok"}}]},
    }
    groups = [
        {
            "probe_group_id": "r1-p1",
            "max_tokens": 100000,
            "variants": [{"variant_id": "r1-p1-v1", "variant_type": "paraphrase", "prompt": "solve"}],
        }
    ]

    with patch("audit_core.deep.services.token_chat", return_value=successful) as mocked:
        execute_variants(
            base_url="https://relay.example/v1",
            token="secret",
            model="reasoning-model",
            round_index=1,
            groups=groups,
            timeout_s=30,
            concurrency=1,
        )

    assert mocked.call_args.kwargs["max_tokens"] == 99999


def test_target_timeout_uses_120_seconds_then_retries_with_a_longer_window():
    timeout = {
        "ok": False,
        "status_code": 0,
        "elapsed_ms": 60_000,
        "failure_kind": "timeout",
        "response": {"error": "read timed out"},
    }
    success = {
        "ok": True,
        "status_code": 200,
        "elapsed_ms": 1_000,
        "response": {"choices": [{"message": {"content": "recovered answer"}}]},
    }
    groups = [{
        "probe_group_id": "r1-p1",
        "max_tokens": 12_000,
        "variants": [{"variant_id": "r1-p1-v1", "variant_type": "boundary", "prompt": "solve"}],
    }]

    with (
        patch("audit_core.deep.services.token_chat", side_effect=[timeout, success]) as mocked,
        patch("audit_core.deep.services.time.sleep") as sleep,
    ):
        responses = execute_variants(
            base_url="https://relay.example/v1",
            token="secret",
            model="reasoning-model",
            round_index=1,
            groups=groups,
            timeout_s=60,
            concurrency=3,
        )

    assert mocked.call_count == 2
    assert mocked.call_args_list[0].kwargs["timeout_s"] == 120.0
    assert mocked.call_args_list[1].kwargs["max_tokens"] == 8_000
    assert mocked.call_args_list[1].kwargs["timeout_s"] == 180.0
    assert sleep.call_count == 1
    assert responses[0]["ok"] is True
    assert responses[0]["retry_count"] == 1
    assert responses[0]["failure_kind"] == ""


def test_target_second_transport_retry_can_wait_up_to_240_seconds():
    timeout = {
        "ok": False,
        "status_code": 0,
        "elapsed_ms": 120_000,
        "failure_kind": "timeout",
        "response": {"error": "read timed out"},
    }
    success = {
        "ok": True,
        "status_code": 200,
        "elapsed_ms": 1_000,
        "response": {"choices": [{"message": {"content": "recovered answer"}}]},
    }
    groups = [{
        "probe_group_id": "r1-p1",
        "max_tokens": 12_000,
        "variants": [{"variant_id": "r1-p1-v1", "variant_type": "boundary", "prompt": "solve"}],
    }]

    with (
        patch("audit_core.deep.services.token_chat", side_effect=[timeout, timeout, success]) as mocked,
        patch("audit_core.deep.services.time.sleep"),
    ):
        responses = execute_variants(
            base_url="https://relay.example/v1",
            token="secret",
            model="reasoning-model",
            round_index=1,
            groups=groups,
            timeout_s=60,
            concurrency=3,
        )

    assert [call.kwargs["timeout_s"] for call in mocked.call_args_list] == [120.0, 180.0, 240.0]
    assert responses[0]["ok"] is True
    assert responses[0]["retry_count"] == 2


def test_transport_gate_allows_partial_scoring_and_marks_network_unstable():
    responses = [
        {"ok": False, "failure_kind": "timeout"},
        {"ok": False, "failure_kind": "connection"},
        {"ok": True, "failure_kind": ""},
    ]

    with patch("audit_core.deep.services.log_event") as event:
        result = ensure_target_transport_integrity(responses)

    assert event.call_args.args[0] == "deep_target_transport_gate"
    assert event.call_args.args[1]["status"] == "partial"
    assert result["valid_responses"] == 1
    assert result["network_unstable"] is True
    assert result["scoring_policy"] == "successful_responses_only"


def test_transport_gate_stops_only_when_no_answer_is_scorable():
    responses = [
        {"ok": False, "failure_kind": "timeout"},
        {"ok": False, "failure_kind": "connection"},
    ]

    with patch("audit_core.deep.services.log_event") as event, pytest.raises(TargetTransportError):
        ensure_target_transport_integrity(responses)

    assert event.call_args.args[1]["status"] == "failed"


def test_audit_judge_uses_dynamic_compact_recovery_after_malformed_output():
    recovered = {
        "semantic_score": 81,
        "ground_truth_alignment_score": 79,
        "group_scores": [],
        "critical_contradictions": [],
        "notes": ["recovered"],
    }
    with (
        patch(
            "audit_core.deep.agents.call_json_agent",
            side_effect=[AgentOutputError("malformed"), recovered],
        ) as agent_call,
        patch("audit_core.deep.agents.log_event") as event,
    ):
        result = AuditJudgeAgent().run(
            config=None,
            ground_truth={"hard_constraints": [], "limitations": []},
            groups=[],
            responses=[],
        )

    assert agent_call.call_count == 2
    assert agent_call.call_args_list[1].kwargs["agent_name"] == "AuditJudgeRecoveryAgent"
    assert result["semantic_score"] == 81
    assert result["ground_truth_alignment_score"] == 79
    assert result["recovered_by"] == "AuditJudgeRecoveryAgent"
    assert [call.args[0] for call in event.call_args_list] == [
        "deep_judge_recovery_start",
        "deep_judge_recovery_end",
    ]


def _ground_truth_evidence():
    return {
        "declared_model_id": "model-x",
        "knowledge_model_id": "model-x",
        "spec_model_id": "model-x",
        "behavior_model_id": "model-x",
        "baseline_kind": "exact",
        "baseline_reason": "exact baseline",
        "collections": {"spec": "specs", "behavior": "behaviors"},
        "spec_evidence": [
            {
                "id": "spec-1",
                "source_level": "P0",
                "claim_type": "tool_use",
                "text": "Official evidence says the model supports structured tool calls.",
                "confidence": 0.95,
            }
        ],
        "claimed_behavior": [
            {
                "id": "claimed-1",
                "task_type": "coding",
                "text": "The response verifies edge cases before presenting code.",
                "confidence": 0.8,
            }
        ],
        "contrast_behavior": [
            {
                "id": "contrast-1",
                "task_type": "coding",
                "text": "The response presents code without edge-case verification.",
                "confidence": 0.7,
            }
        ],
    }


def test_ground_truth_uses_recovery_agent_after_malformed_primary_output():
    recovered = {
        "hard_constraints": [],
        "behavior_signatures": [],
        "discriminative_features": [],
        "limitations": ["recovered"],
        "recommended_dimensions": [],
    }
    with (
        patch(
            "audit_core.deep.agents.call_json_agent",
            side_effect=[AgentOutputError("malformed"), recovered],
        ) as agent_call,
        patch("audit_core.deep.agents.log_event") as event,
    ):
        result = GroundTruthCuratorAgent().run(config=None, evidence=_ground_truth_evidence())

    assert agent_call.call_count == 2
    assert agent_call.call_args_list[1].kwargs["agent_name"] == "GroundTruthRecoveryAgent"
    assert result["ground_truth_source"] == "GroundTruthRecoveryAgent"
    assert result["coverage"] > 0
    assert [call.args[0] for call in event.call_args_list] == [
        "deep_ground_truth_recovery_start",
        "deep_ground_truth_recovery_end",
    ]
    assert event.call_args_list[-1].args[1]["method"] == "recovery_agent"


def test_ground_truth_recovery_runs_after_three_malformed_model_responses():
    invalid = {"response": {"choices": [{"message": {"content": "not-json"}}]}}
    recovered_payload = {
        "hard_constraints": [],
        "behavior_signatures": [],
        "discriminative_features": [],
        "limitations": ["recovered after retries"],
        "recommended_dimensions": [],
    }
    recovered = {
        "response": {
            "choices": [
                {"message": {"content": json.dumps(recovered_payload)}}
            ]
        }
    }
    config = AuditConfig(
        deepseek_base_url="https://auditor.example/v1",
        deepseek_api_key="secret",
        deepseek_model="auditor-model",
        deepseek_temperature=0.1,
        deepseek_max_tokens=3500,
        request_timeout_s=10,
        export_dir="reports",
    )
    with (
        patch(
            "audit_core.deep.llm.deepseek_chat",
            side_effect=[invalid, invalid, invalid, recovered],
        ) as chat,
        patch("audit_core.deep.llm.log_event"),
        patch("audit_core.deep.agents.log_event"),
    ):
        result = GroundTruthCuratorAgent().run(config=config, evidence=_ground_truth_evidence())

    assert chat.call_count == 4
    assert result["ground_truth_source"] == "GroundTruthRecoveryAgent"
    assert result["limitations"] == ["recovered after retries"]


def test_ground_truth_falls_back_to_retrieved_evidence_when_recovery_is_malformed():
    with (
        patch(
            "audit_core.deep.agents.call_json_agent",
            side_effect=[AgentOutputError("primary malformed"), AgentOutputError("recovery malformed")],
        ),
        patch("audit_core.deep.agents.log_event") as event,
    ):
        result = GroundTruthCuratorAgent().run(config=None, evidence=_ground_truth_evidence())

    assert result["ground_truth_source"] == "deterministic_evidence_fallback"
    assert result["hard_constraints"][0]["expected"].startswith("Official evidence")
    assert result["hard_constraints"][0]["evidence_ids"] == ["spec-1"]
    assert result["behavior_signatures"][0]["evidence_ids"] == ["claimed-1", "contrast-1"]
    assert "structured tool calls" in result["hard_constraints"][0]["expected"]
    assert event.call_args_list[-1].args[1]["method"] == "deterministic_evidence_fallback"


def test_deep_report_contains_questions_answers_judges_and_red_team_evidence():
    inp = OrchestratorInput(
        token_id=7,
        audited_token="secret",
        platform="relay",
        token_base_url="https://relay.example/v1",
        claimed_model="model-x",
        non_claimed_model="",
        audit_time="2026-08-25 10:00:00",
    )
    ground_truth = {
        "coverage": 1.0,
        "retrieval": {
            "spec_model_id": "model-x",
            "behavior_model_id": "model-x",
            "baseline_kind": "exact",
        },
        "evidence_counts": {"spec": 5, "claimed_behavior": 8, "contrast_behavior": 8},
        "hard_constraints": [
            {"feature": "api_field", "expected": "field-x", "confidence": 0.9, "evidence_ids": ["spec-1"]}
        ],
        "behavior_signatures": [
            {"feature": "style", "expected": "structured", "contrast": "terse", "evidence_ids": ["behavior-1"]}
        ],
        "limitations": ["sample limitation"],
    }
    rounds = [
        {
            "round": 1,
            "probe_groups": [
                {
                    "probe_group_id": "r1-p1",
                    "dimension": "coding",
                    "prompt": "MOTHER QUESTION",
                    "why_discriminative": "reason",
                    "invariants": ["same intent"],
                    "rubric": ["correct"],
                    "max_tokens": 100000,
                    "variants": [
                        {"variant_id": "r1-p1-v1", "variant_type": "paraphrase", "prompt": "FUZZ QUESTION"}
                    ],
                }
            ],
            "responses": [
                {
                    "variant_id": "r1-p1-v1",
                    "ok": True,
                    "status_code": 200,
                    "elapsed_ms": 123,
                    "retry_count": 0,
                    "response_text": "TARGET ANSWER",
                    "error": "",
                }
            ],
            "objective": {
                "score": 90,
                "groups": [{"probe_group_id": "r1-p1", "variant_results": [{"variant_id": "r1-p1-v1", "score": 100}]}],
            },
            "audit_judgement": {
                "semantic_score": 88,
                "ground_truth_alignment_score": 86,
                "group_scores": [
                    {"probe_group_id": "r1-p1", "semantic_score": 88, "ground_truth_alignment_score": 86, "reasons": ["JUDGE REASON"]}
                ],
            },
            "behavior_judgement": {
                "behavior_score": 80,
                "claimed_similarity": 0.8,
                "strongest_contrast_similarity": 0.3,
                "similarity_margin": 0.5,
                "discriminative_observations": ["BEHAVIOR OBSERVATION"],
            },
            "consistency_judgement": {
                "consistency_score": 92,
                "routing_instability_suspected": False,
                "routing_evidence": ["ROUTING EVIDENCE"],
                "group_consistency": [{"probe_group_id": "r1-p1", "score": 92, "reasons": ["CONSISTENCY REASON"]}],
            },
        }
    ]
    score = {
        "total_score": 86.5,
        "band": "consistent",
        "confidence": 0.85,
        "components": {"objective": 90},
    }
    red_team = {
        "material_alternative_explanations": ["ALTERNATIVE EXPLANATION"],
        "unresolved_contradictions": ["UNRESOLVED CONTRADICTION"],
        "should_cap_confidence": True,
        "confidence_cap": 0.85,
        "review_conclusion": "RED TEAM CONCLUSION",
    }
    decision = {
        "overall_conclusion": "FINAL CONCLUSION",
        "evidence_for": ["SUPPORTING EVIDENCE"],
        "evidence_against": ["LIMITING EVIDENCE"],
    }

    report = build_deep_report_markdown(
        inp=inp,
        settings=DeepAuditSettings(rounds=1),
        ground_truth=ground_truth,
        rounds=rounds,
        score=score,
        red_team=red_team,
        decision=decision,
        stopped_early=False,
    )

    for expected in (
        "母题原文",
        "MOTHER QUESTION",
        "FUZZ QUESTION",
        "TARGET ANSWER",
        "JUDGE REASON",
        "CONSISTENCY REASON",
        "BEHAVIOR OBSERVATION",
        "ROUTING EVIDENCE",
        "ALTERNATIVE EXPLANATION",
        "UNRESOLVED CONTRADICTION",
        "100000 Token",
    ):
        assert expected in report


def test_normalizes_consistency_judge_fractional_scale():
    output = _normalize_consistency_output(
        {
            "consistency_score": 0.73,
            "group_consistency": [
                {"probe_group_id": "a", "score": 1.0},
                {"probe_group_id": "b", "score": 0.2},
            ],
        }
    )

    assert output["consistency_score"] == 73.0
    assert output["group_consistency"][0]["score"] == 100.0
    assert output["group_consistency"][1]["score"] == 20.0
