from __future__ import annotations

from typing import Any

from audit_core.scripts.token_api import token_chat
from audit_core.utils import log_event


def run_relay_preflight(
    *,
    base_url: str,
    token: str,
    model: str,
    timeout_s: float,
) -> dict[str, Any]:
    log_event(
        "preflight_start",
        {
            "phase": "preflight",
            "model": model,
            "base_url": base_url,
        },
    )
    response = token_chat(
        base_url=base_url,
        token=token,
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        timeout_s=min(max(1.0, timeout_s), 20.0),
        max_tokens=8,
    )
    status_code = int(response.get("status_code") or 0)
    response_shape_ok = _has_compatible_response(response)
    passed = bool(response.get("ok")) and response_shape_ok
    message = "中转站连接、鉴权及声明模型校验通过" if passed else _safe_preview(response, token)
    reason = "connected" if passed else _failure_reason(status_code, response_shape_ok, message)
    if not message and not passed:
        message = _default_message(reason)

    result = {
        "passed": passed,
        "status": "passed" if passed else "failed",
        "status_code": status_code,
        "elapsed_ms": int(response.get("elapsed_ms") or 0),
        "endpoint": response.get("endpoint") or "chat_completions",
        "url": response.get("url") or "",
        "model": model,
        "reason": reason,
        "message": message,
    }
    log_event("preflight_end", {"phase": "preflight", **result})
    return result


def _has_compatible_response(response: dict[str, Any]) -> bool:
    if not response.get("ok"):
        return False
    data = response.get("response")
    if not isinstance(data, dict):
        return False
    endpoint = response.get("endpoint")
    if endpoint == "responses":
        return isinstance(data.get("output"), list) or isinstance(data.get("output_text"), str)
    choices = data.get("choices")
    return isinstance(choices, list) and bool(choices)


def _failure_reason(status_code: int, response_shape_ok: bool, message: str = "") -> str:
    normalized_message = message.casefold()
    if 200 <= status_code < 300 and not response_shape_ok:
        return "incompatible_response"
    if status_code == 0:
        return "network_unreachable"
    if status_code == 401:
        return "authentication_failed"
    if status_code == 403:
        region_markers = ("region", "country", "地区", "区域", "地域", "国家")
        if any(marker in normalized_message for marker in region_markers):
            return "region_restricted"
        model_markers = ("model", "模型")
        if any(marker in normalized_message for marker in model_markers):
            return "model_access_denied"
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
    return "relay_preflight_failed"


def _safe_preview(response: dict[str, Any], token: str, limit: int = 300) -> str:
    data = response.get("response")
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
    value = value.replace(token, "[REDACTED]") if token else value
    return value[:limit]


def _default_message(reason: str) -> str:
    messages = {
        "network_unreachable": "无法连接中转站，请检查 Base URL、网络或 TLS 配置",
        "authentication_failed": "中转站拒绝鉴权，请检查 Token 是否有效",
        "region_restricted": "当前模型在请求所在地区不可用，请更换模型或上游线路",
        "model_access_denied": "当前 Token 无权访问声明模型，或该模型在中转站不可用",
        "access_forbidden": "中转站拒绝访问，请检查 Token 权限、账号策略或上游限制",
        "endpoint_or_model_not_found": "接口或声明模型不存在",
        "rate_limited_or_quota_exhausted": "中转站限流或额度不足，当前无法执行审计",
        "request_timeout": "中转站预检请求超时",
        "upstream_unavailable": "中转站或其上游服务不可用",
        "invalid_request_or_model": "中转站拒绝请求，请检查声明模型和兼容接口",
        "incompatible_response": "中转站返回内容不符合 OpenAI 兼容格式",
    }
    return messages.get(reason, "中转站预检失败")
