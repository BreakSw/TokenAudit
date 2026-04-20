from __future__ import annotations

import re
import time
from typing import Any

import requests


_GPT5_RE = re.compile(r"^gpt-5(\.|$)", re.IGNORECASE)


def _join_openai_path(base_url: str, path: str) -> str:
    b = (base_url or "").strip()
    if not b:
        return ""
    b = b.rstrip("/")
    if b.endswith("/v1/chat/completions") or b.endswith("/v1/responses") or b.endswith("/v1/models"):
        return b
    if b.endswith("/v1"):
        return b + path
    return b + "/v1" + path


def token_responses(
    *,
    base_url: str,
    token: str | None,
    model: str,
    messages: list[dict[str, str]],
    timeout_s: float = 60,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = _join_openai_path(base_url, "/responses")
    if not url:
        return {"status_code": 0, "elapsed_ms": 0, "response": {"error": "token_base_url is empty"}, "ok": False, "endpoint": "responses"}

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    input_text = "\n".join([(m.get("content") or "") for m in messages if isinstance(m, dict)])
    payload = {
        "model": (model or "").strip(),
        "input": input_text,
        "temperature": 0.2,
        "max_output_tokens": 1024,
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
            "endpoint": "responses",
            "url": url,
        }
    except Exception as e:
        return {
            "status_code": 0,
            "elapsed_ms": int((time.perf_counter() - start) * 1000),
            "response": {"error": str(e)},
            "ok": False,
            "endpoint": "responses",
            "url": url,
        }


def token_models(
    *,
    base_url: str,
    token: str | None,
    timeout_s: float = 20,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = _join_openai_path(base_url, "/models")
    if not url:
        return {"status_code": 0, "elapsed_ms": 0, "response": {"error": "token_base_url is empty"}, "ok": False, "endpoint": "models", "url": ""}

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    start = time.perf_counter()
    try:
        resp = requests.get(url, headers=headers, timeout=timeout_s)
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
            "endpoint": "models",
            "url": url,
        }
    except Exception as e:
        return {
            "status_code": 0,
            "elapsed_ms": int((time.perf_counter() - start) * 1000),
            "response": {"error": str(e)},
            "ok": False,
            "endpoint": "models",
            "url": url,
        }


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
            "endpoint": "chat_completions",
            "url": "",
        }

    model_name = (model or "").strip()
    if _GPT5_RE.match(model_name):
        resp = token_responses(
            base_url=base_url,
            token=token,
            model=model_name,
            messages=messages,
            timeout_s=timeout_s,
            extra_headers=extra_headers,
        )
        if resp.get("ok"):
            return resp

    url = _join_openai_path(base_url, "/chat/completions")
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    payload = {
        "model": model_name,
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

        out = {
            "status_code": resp.status_code,
            "elapsed_ms": elapsed_ms,
            "response": data,
            "ok": 200 <= resp.status_code < 300,
            "endpoint": "chat_completions",
            "url": url,
        }
        if not out["ok"] and _GPT5_RE.match(model_name):
            resp2 = token_responses(
                base_url=base_url,
                token=token,
                model=model_name,
                messages=messages,
                timeout_s=timeout_s,
                extra_headers=extra_headers,
            )
            if resp2.get("ok"):
                return resp2
        return out
    except Exception as e:
        return {
            "status_code": 0,
            "elapsed_ms": int((time.perf_counter() - start) * 1000),
            "response": {"error": str(e)},
            "ok": False,
            "endpoint": "chat_completions",
            "url": url,
        }
