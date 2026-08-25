from __future__ import annotations

from dataclasses import replace
import json
from typing import Any

from audit_core.config import AuditConfig
from audit_core.scripts.deepseek_api import DeepSeekError, deepseek_chat
from audit_core.utils import coerce_json_object, log_event


class AgentOutputError(RuntimeError):
    pass


def call_json_agent(
    *,
    config: AuditConfig,
    agent_name: str,
    system_prompt: str,
    payload: dict[str, Any],
    temperature: float,
    max_tokens: int = 3000,
    required_keys: tuple[str, ...] = (),
) -> dict[str, Any]:
    log_event("deep_agent_start", {"agent": agent_name})
    agent_config = replace(config, deepseek_temperature=temperature)
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, sort_keys=True),
        },
    ]
    last_error: AgentOutputError | None = None
    for attempt in range(3):
        retry_messages = messages
        if attempt:
            retry_messages = messages + [
                {
                    "role": "user",
                    "content": "The previous response had no usable final JSON. Return the required JSON object now, with no analysis or markdown.",
                }
            ]
        request_max_tokens = max_tokens if not attempt else max(max_tokens * 2, 8000)
        try:
            result = deepseek_chat(
                config=agent_config,
                messages=retry_messages,
                max_tokens=request_max_tokens,
                json_response=True,
            )
        except DeepSeekError as exc:
            if exc.status_code != 400:
                log_event(
                    "deep_agent_end",
                    {
                        "agent": agent_name,
                        "status": "error",
                        "attempt": attempt + 1,
                        "reason": exc.reason,
                        "status_code": exc.status_code,
                        "elapsed_ms": exc.elapsed_ms,
                    },
                )
                raise
            try:
                result = deepseek_chat(
                    config=agent_config,
                    messages=retry_messages,
                    max_tokens=request_max_tokens,
                    json_response=False,
                )
            except DeepSeekError as fallback_exc:
                log_event(
                    "deep_agent_end",
                    {
                        "agent": agent_name,
                        "status": "error",
                        "attempt": attempt + 1,
                        "reason": fallback_exc.reason,
                        "status_code": fallback_exc.status_code,
                        "elapsed_ms": fallback_exc.elapsed_ms,
                    },
                )
                raise
        try:
            parsed = {"raw_text": ""}
            missing: list[str] = list(required_keys)
            for content in _chat_content_candidates(result):
                candidate = coerce_json_object(content)
                if "raw_text" in candidate:
                    continue
                candidate_missing = [key for key in required_keys if key not in candidate]
                parsed = candidate
                missing = candidate_missing
                if not candidate_missing:
                    break
            if "raw_text" in parsed:
                raise AgentOutputError(f"{agent_name} did not return valid JSON")
            if missing:
                raise AgentOutputError(f"{agent_name} missing required keys: {', '.join(missing)}")
            log_event("deep_agent_end", {"agent": agent_name, "status": "success", "attempt": attempt + 1})
            return parsed
        except AgentOutputError as exc:
            last_error = exc
    assert last_error is not None
    log_event(
        "deep_agent_end",
        {
            "agent": agent_name,
            "status": "error",
            "attempt": 3,
            "reason": "invalid_agent_output",
            "message": str(last_error)[:300],
        },
    )
    raise last_error


def _chat_content(result: dict[str, Any]) -> str:
    return _chat_content_candidates(result)[0]


def _chat_content_candidates(result: dict[str, Any]) -> list[str]:
    response = result.get("response")
    if not isinstance(response, dict):
        raise AgentOutputError("audit model returned no response object")
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise AgentOutputError("audit model returned no choices")
    first = choices[0]
    message = first.get("message") if isinstance(first, dict) else None
    candidates: list[str] = []
    if isinstance(message, dict):
        for key in ("content", "final", "reasoning_content", "reasoning"):
            content = _content_text(message.get(key))
            if content and content not in candidates:
                candidates.append(content)
    if isinstance(first, dict):
        choice_text = _content_text(first.get("text"))
        if choice_text and choice_text not in candidates:
            candidates.append(choice_text)
    output_text = _content_text(response.get("output_text"))
    if output_text and output_text not in candidates:
        candidates.append(output_text)
    if candidates:
        return candidates
    raise AgentOutputError("audit model returned empty content")


def _content_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()
    return ""
