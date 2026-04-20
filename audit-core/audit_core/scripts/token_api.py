from __future__ import annotations

import time
from typing import Any

import requests


def token_chat(
    *,
    base_url: str,
    token: str | None,
    model: str,
    messages: list[dict[str, str]],
    timeout_s: float = 60,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not base_url:
        return {
            "status_code": 0,
            "elapsed_ms": 0,
            "response": {"error": "token_base_url is empty"},
            "ok": False,
        }

    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1024,
    }
    start = time.perf_counter()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        content_type = resp.headers.get("content-type", "")
        try:
            data = resp.json() if "json" in content_type.lower() else {"text": resp.text}
        except Exception:
            data = {"text": resp.text}

        return {
            "status_code": resp.status_code,
            "elapsed_ms": elapsed_ms,
            "response": data,
            "ok": 200 <= resp.status_code < 300,
        }
    except Exception as e:
        return {
            "status_code": 0,
            "elapsed_ms": int((time.perf_counter() - start) * 1000),
            "response": {"error": str(e)},
            "ok": False,
        }
