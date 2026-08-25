from __future__ import annotations

import time
from typing import Any

import requests

from audit_core.config import AuditConfig


class DeepSeekError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        reason: str,
        status_code: int = 0,
        elapsed_ms: int = 0,
        url: str = "",
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.status_code = status_code
        self.elapsed_ms = elapsed_ms
        self.url = url


def normalize_chat_completions_url(base_url: str) -> str:
    """Accept an OpenAI-compatible service root, /v1 base, or full endpoint."""
    value = (base_url or "").strip().rstrip("/")
    if not value:
        return ""

    lowered = value.casefold()
    for suffix in ("/chat/completions", "/responses", "/models"):
        if lowered.endswith(suffix):
            return value[: -len(suffix)] + "/chat/completions"
    if lowered.endswith("/v1"):
        return value + "/chat/completions"
    return value + "/v1/chat/completions"


def deepseek_chat(
    *,
    config: AuditConfig,
    messages: list[dict[str, str]],
    sensitive_values: list[str] | None = None,
    timeout_s: float | None = None,
    max_tokens: int | None = None,
    json_response: bool = False,
) -> dict[str, Any]:
    if not config.deepseek_api_key:
        raise DeepSeekError(
            "audit_ai_api_key_missing",
            reason="authentication_not_configured",
        )

    url = normalize_chat_completions_url(config.deepseek_base_url)
    if not url:
        raise DeepSeekError(
            "audit_ai_url_missing",
            reason="endpoint_not_configured",
        )

    safe_messages = _redact_messages(messages, sensitive_values or [])
    payload = {
        "model": config.deepseek_model,
        "temperature": config.deepseek_temperature,
        "max_tokens": config.deepseek_max_tokens if max_tokens is None else max(1, int(max_tokens)),
        "messages": safe_messages,
    }
    if json_response:
        payload["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {config.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    start = time.perf_counter()
    resp = None
    last_network_error: requests.RequestException | None = None
    for network_attempt in range(2):
        try:
            resp = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=config.request_timeout_s if timeout_s is None else max(1.0, float(timeout_s)),
            )
            break
        except requests.RequestException as exc:
            last_network_error = exc
            if network_attempt == 0:
                time.sleep(1.0)
    if resp is None:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        assert last_network_error is not None
        raise DeepSeekError(
            _safe_error_text(str(last_network_error), config.deepseek_api_key),
            reason="network_unreachable",
            elapsed_ms=elapsed_ms,
            url=url,
        ) from last_network_error
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    content_type = resp.headers.get("content-type", "")
    try:
        data = resp.json() if "json" in content_type.lower() else {"text": resp.text}
    except Exception:
        data = {"text": resp.text}

    if resp.status_code >= 400:
        raise DeepSeekError(
            _response_error_message(data, config.deepseek_api_key) or f"status={resp.status_code}",
            reason=_failure_reason(resp.status_code),
            status_code=resp.status_code,
            elapsed_ms=elapsed_ms,
            url=url,
        )

    if not _has_chat_completion(data):
        raise DeepSeekError(
            "audit_ai_incompatible_response",
            reason="incompatible_response",
            status_code=resp.status_code,
            elapsed_ms=elapsed_ms,
            url=url,
        )

    return {
        "ok": True,
        "status_code": resp.status_code,
        "elapsed_ms": elapsed_ms,
        "response": data,
        "endpoint": "chat_completions",
        "url": url,
    }


def _redact_messages(messages: list[dict[str, str]], sensitive_values: list[str]) -> list[dict[str, str]]:
    secrets = sorted({value for value in sensitive_values if value}, key=len, reverse=True)
    safe: list[dict[str, str]] = []
    for message in messages:
        next_message = dict(message)
        content = next_message.get("content")
        if isinstance(content, str):
            for secret in secrets:
                content = content.replace(secret, "[REDACTED]")
            next_message["content"] = content
        safe.append(next_message)
    return safe


def _has_chat_completion(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        return False
    first = choices[0]
    if not isinstance(first, dict):
        return False
    message = first.get("message")
    if not isinstance(message, dict):
        return False
    return (
        isinstance(message.get("content"), (str, list))
        or isinstance(message.get("reasoning_content"), str)
        or isinstance(message.get("reasoning"), str)
    )


def _failure_reason(status_code: int) -> str:
    if status_code == 401:
        return "authentication_failed"
    if status_code == 403:
        return "access_forbidden"
    if status_code == 404:
        return "endpoint_or_model_not_found"
    if status_code == 429:
        return "rate_limited_or_quota_exhausted"
    if status_code in (408, 504):
        return "request_timeout"
    if status_code >= 500:
        return "upstream_unavailable"
    if status_code == 400:
        return "invalid_request_or_model"
    return "audit_ai_request_failed"


def _response_error_message(data: Any, api_key: str, limit: int = 300) -> str:
    value = ""
    if isinstance(data, dict):
        error = data.get("error")
        if isinstance(error, dict):
            value = str(error.get("message") or error.get("code") or "")
        elif isinstance(error, str):
            value = error
        elif isinstance(data.get("message"), str):
            value = data["message"]
        elif isinstance(data.get("text"), str):
            value = data["text"]
    return _safe_error_text(value, api_key)[:limit]


def _safe_error_text(value: str, api_key: str) -> str:
    return value.replace(api_key, "[REDACTED]") if api_key else value
