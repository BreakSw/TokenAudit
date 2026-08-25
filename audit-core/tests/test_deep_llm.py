from unittest.mock import patch

import pytest

from audit_core.config import AuditConfig
from audit_core.deep.llm import AgentOutputError, _chat_content, call_json_agent


def _wrapped(message):
    return {"response": {"choices": [{"message": message}]}}


def _config():
    return AuditConfig(
        deepseek_base_url="https://auditor.example/v1",
        deepseek_api_key="secret",
        deepseek_model="auditor-model",
        deepseek_temperature=0.2,
        deepseek_max_tokens=1000,
        request_timeout_s=10,
        export_dir="reports",
    )


def test_reads_standard_chat_content():
    assert _chat_content(_wrapped({"content": '{"ok": true}'})) == '{"ok": true}'


def test_reads_reasoning_provider_fallback_when_content_is_empty():
    result = _wrapped({"content": "", "reasoning_content": '{"ok": true}'})
    assert _chat_content(result) == '{"ok": true}'


def test_reads_structured_content_parts():
    result = _wrapped({"content": [{"type": "text", "text": '{"ok": true}'}]})
    assert _chat_content(result) == '{"ok": true}'


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("说明如下：\n```json\n{\"score\": 91}\n```\n完成。", 91),
        ("draft={\"ignored\": true}\nfinal={\"score\": 82}", 82),
        ("{“score”: 73,}", 73),
        ('{"score": 64, "notes": ["usable"]', 64),
    ],
)
def test_agent_recovers_common_json_format_variants(content, expected):
    with patch("audit_core.deep.llm.deepseek_chat", return_value=_wrapped({"content": content})):
        result = call_json_agent(
            config=_config(),
            agent_name="JudgeAgent",
            system_prompt="Return JSON.",
            payload={},
            temperature=0.0,
            required_keys=("score",),
        )

    assert result["score"] == expected


def test_agent_checks_reasoning_when_visible_content_is_not_json():
    response = _wrapped({"content": "I could not format the result.", "reasoning_content": '{"score": 88}'})
    with patch("audit_core.deep.llm.deepseek_chat", return_value=response):
        result = call_json_agent(
            config=_config(),
            agent_name="JudgeAgent",
            system_prompt="Return JSON.",
            payload={},
            temperature=0.0,
            required_keys=("score",),
        )

    assert result["score"] == 88


def test_agent_failure_emits_terminal_end_fact():
    config = _config()
    invalid = _wrapped({"content": "not-json"})

    with (
        patch("audit_core.deep.llm.deepseek_chat", return_value=invalid),
        patch("audit_core.deep.llm.log_event") as event,
        pytest.raises(AgentOutputError),
    ):
        call_json_agent(
            config=config,
            agent_name="JudgeAgent",
            system_prompt="Return JSON.",
            payload={},
            temperature=0.2,
            required_keys=("score",),
        )

    assert event.call_args_list[0].args[0] == "deep_agent_start"
    assert event.call_args_list[-1].args[0] == "deep_agent_end"
    assert event.call_args_list[-1].args[1]["status"] == "error"
    assert event.call_args_list[-1].args[1]["reason"] == "invalid_agent_output"
