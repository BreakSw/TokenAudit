from __future__ import annotations

from typing import Any

from audit_core.config import AuditConfig
from audit_core.scripts.deepseek_api import DeepSeekError, deepseek_chat
from audit_core.utils import log_event


def run_audit_ai_preflight(*, config: AuditConfig) -> dict[str, Any]:
    log_event(
        "audit_ai_preflight_start",
        {"phase": "audit_ai_preflight", "model": config.deepseek_model},
    )
    try:
        response = deepseek_chat(
            config=config,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            timeout_s=min(max(1.0, config.request_timeout_s), 20.0),
            max_tokens=8,
        )
        result = {
            "passed": True,
            "status": "passed",
            "reason": "connected",
            "status_code": int(response.get("status_code") or 0),
            "elapsed_ms": int(response.get("elapsed_ms") or 0),
            "endpoint": response.get("endpoint") or "chat_completions",
            "url": response.get("url") or "",
            "model": config.deepseek_model,
            "message": "",
        }
    except DeepSeekError as error:
        result = {
            "passed": False,
            "status": "failed",
            "reason": error.reason,
            "status_code": error.status_code,
            "elapsed_ms": error.elapsed_ms,
            "endpoint": "chat_completions",
            "url": error.url,
            "model": config.deepseek_model,
            "message": str(error)[:300],
        }

    log_event("audit_ai_preflight_end", {"phase": "audit_ai_preflight", **result})
    return result
