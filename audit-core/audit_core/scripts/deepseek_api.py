from __future__ import annotations

import time
from typing import Any

import requests

from audit_core.config import AuditConfig


class DeepSeekError(RuntimeError):
    pass


def deepseek_chat(*, config: AuditConfig, messages: list[dict[str, str]]) -> dict[str, Any]:
    if not config.deepseek_api_key:
        return {"elapsed_ms": 0, "response": {"error": "DEEPSEEK_API_KEY is not set"}}

    payload = {
        "model": config.deepseek_model,
        "temperature": config.deepseek_temperature,
        "max_tokens": config.deepseek_max_tokens,
        "messages": messages,
    }
    headers = {
        "Authorization": f"Bearer {config.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    start = time.perf_counter()
    try:
        resp = requests.post(
            config.deepseek_base_url,
            json=payload,
            headers=headers,
            timeout=config.request_timeout_s,
        )
    except Exception as e:
        return {"elapsed_ms": int((time.perf_counter() - start) * 1000), "response": {"error": str(e)}}
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    content_type = resp.headers.get("content-type", "")
    try:
        data = resp.json() if "json" in content_type.lower() else {"text": resp.text}
    except Exception:
        data = {"text": resp.text}

    if resp.status_code >= 400:
        return {"elapsed_ms": elapsed_ms, "response": {"error": f"status={resp.status_code}", "body": data}}

    return {"elapsed_ms": elapsed_ms, "response": data}
