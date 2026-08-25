from __future__ import annotations

import json
import time
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests


def _join_openai_path(base_url: str, path: str) -> str:
    raw = (base_url or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw)
    base_path = parsed.path.rstrip("/")
    lowered = base_path.casefold()
    for suffix in ("/chat/completions", "/responses", "/models"):
        if lowered.endswith(suffix):
            target_path = base_path[: -len(suffix)] + path
            break
    else:
        target_path = base_path + path if lowered.endswith("/v1") else base_path + "/v1" + path
    return urlunsplit((parsed.scheme, parsed.netloc, target_path, parsed.query, parsed.fragment))


def _openai_path_candidates(base_url: str, path: str) -> list[str]:
    primary = _join_openai_path(base_url, path)
    if not primary:
        return []
    parsed = urlsplit((base_url or "").strip())
    base_path = parsed.path.rstrip("/")
    explicit_endpoint = any(
        base_path.casefold().endswith(suffix)
        for suffix in ("/chat/completions", "/responses", "/models")
    )
    candidates = [primary]
    if not explicit_endpoint and not base_path.casefold().endswith("/v1"):
        without_v1 = urlunsplit(
            (parsed.scheme, parsed.netloc, base_path + path, parsed.query, parsed.fragment)
        )
        if without_v1 not in candidates:
            candidates.append(without_v1)
    return candidates


def _uses_responses_endpoint(api_url: str) -> bool:
    return (api_url or "").strip().rstrip("/").casefold().endswith("/responses")


def token_responses(
    *,
    base_url: str,
    token: str | None,
    model: str,
    messages: list[dict[str, str]],
    timeout_s: float = 60,
    max_tokens: int = 1024,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = _join_openai_path(base_url, "/responses")
    if not url:
        return {"status_code": 0, "elapsed_ms": 0, "response": {"error": "token_base_url is empty"}, "ok": False, "endpoint": "responses"}

    headers = _headers(token, extra_headers)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)

    input_text = "\n".join([(m.get("content") or "") for m in messages if isinstance(m, dict)])
    payload = {
        "model": (model or "").strip(),
        "input": input_text,
        "temperature": 0.2,
        "max_output_tokens": max(1, int(max_tokens)),
    }

    request_payload = payload
    total_elapsed_ms = 0
    for payload_attempt in range(2):
        start = time.perf_counter()
        try:
            resp = requests.post(url, json=request_payload, headers=headers, timeout=(10.0, timeout_s))
            total_elapsed_ms += int((time.perf_counter() - start) * 1000)
            result = {
                "status_code": resp.status_code,
                "elapsed_ms": total_elapsed_ms,
                "response": _decode_response(resp),
                "ok": 200 <= resp.status_code < 300,
                "endpoint": "responses",
                "url": url,
                "payload_fallback_used": payload_attempt > 0,
            }
        except Exception as e:
            return {
                "status_code": 0,
                "elapsed_ms": total_elapsed_ms + int((time.perf_counter() - start) * 1000),
                "response": {"error": str(e)},
                "ok": False,
                "endpoint": "responses",
                "url": url,
                "failure_kind": _exception_kind(e),
                "payload_fallback_used": payload_attempt > 0,
            }
        fallback = _compatible_payload_fallback(request_payload, result)
        if fallback is None or payload_attempt >= 1:
            return result
        request_payload = fallback
    return result


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

    headers = _headers(token, extra_headers)

    start = time.perf_counter()
    try:
        resp = requests.get(url, headers=headers, timeout=(10.0, timeout_s))
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        data = _decode_response(resp)

        return {
            "status_code": resp.status_code,
            "elapsed_ms": elapsed_ms,
            "response": data,
            "ok": 200 <= resp.status_code < 300,
            "endpoint": "models",
            "url": url,
            "failure_kind": _exception_kind(e),
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
    max_tokens: int = 1024,
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
    if _uses_responses_endpoint(base_url):
        return token_responses(
            base_url=base_url,
            token=token,
            model=model_name,
            messages=messages,
            timeout_s=timeout_s,
            max_tokens=max_tokens,
            extra_headers=extra_headers,
        )

    urls = _openai_path_candidates(base_url, "/chat/completions")
    headers = _headers(token, extra_headers)

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max(1, int(max_tokens)),
    }
    last_result: dict[str, Any] | None = None
    for index, url in enumerate(urls):
        request_payload = payload
        for payload_attempt in range(3):
            start = time.perf_counter()
            try:
                resp = requests.post(url, json=request_payload, headers=headers, timeout=(10.0, timeout_s))
                elapsed_ms = int((time.perf_counter() - start) * 1000)
                result = {
                    "status_code": resp.status_code,
                    "elapsed_ms": elapsed_ms,
                    "response": _decode_response(resp),
                    "ok": 200 <= resp.status_code < 300,
                    "endpoint": "chat_completions",
                    "url": url,
                    "path_fallback_used": index > 0,
                    "payload_fallback_used": payload_attempt > 0,
                    "retry_after_s": _retry_after_seconds(resp.headers.get("retry-after")),
                }
            except Exception as e:
                result = {
                    "status_code": 0,
                    "elapsed_ms": int((time.perf_counter() - start) * 1000),
                    "response": {"error": str(e)},
                    "ok": False,
                    "endpoint": "chat_completions",
                    "url": url,
                    "failure_kind": _exception_kind(e),
                    "path_fallback_used": index > 0,
                    "payload_fallback_used": payload_attempt > 0,
                }
            fallback = _compatible_payload_fallback(request_payload, result)
            if fallback is None or payload_attempt >= 2:
                break
            request_payload = fallback
        last_result = result
        if result["ok"] or int(result["status_code"] or 0) not in {404, 405}:
            return result
    return last_result or {
        "status_code": 0,
        "elapsed_ms": 0,
        "response": {"error": "no compatible endpoint candidate"},
        "ok": False,
        "endpoint": "chat_completions",
        "url": "",
        "failure_kind": "protocol",
    }


def _headers(token: str | None, extra_headers: dict[str, str] | None) -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "TokenAudit/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)
    return headers


def _decode_response(response: Any) -> dict[str, Any]:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return _unwrap_payload(payload)
    except Exception:
        pass
    text = str(getattr(response, "text", "") or "").strip()
    if not text:
        return {"text": ""}
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return _unwrap_payload(payload)
    except Exception:
        pass
    streamed = _decode_sse(text)
    return streamed if streamed is not None else {"text": text}


def _unwrap_payload(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("data", "result"):
        nested = payload.get(key)
        if isinstance(nested, dict) and any(name in nested for name in ("choices", "output", "output_text", "error")):
            return nested
    return payload


def _decode_sse(text: str) -> dict[str, Any] | None:
    content_parts: list[str] = []
    last_payload: dict[str, Any] | None = None
    for line in text.splitlines():
        if not line.lstrip().startswith("data:"):
            continue
        raw = line.split(":", 1)[1].strip()
        if not raw or raw == "[DONE]":
            continue
        try:
            payload = json.loads(raw)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        last_payload = payload
        choices = payload.get("choices")
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            choice = choices[0]
            delta = choice.get("delta") if isinstance(choice.get("delta"), dict) else {}
            message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
            value = delta.get("content") or message.get("content") or choice.get("text")
            if isinstance(value, str):
                content_parts.append(value)
        delta_text = payload.get("delta")
        if str(payload.get("type") or "").endswith("output_text.delta") and isinstance(delta_text, str):
            content_parts.append(delta_text)
    if content_parts:
        return {"choices": [{"message": {"content": "".join(content_parts)}}]}
    return _unwrap_payload(last_payload) if last_payload is not None else None


def _exception_kind(error: Exception) -> str:
    if isinstance(error, requests.Timeout):
        return "timeout"
    if isinstance(error, requests.ConnectionError):
        return "connection"
    return "network"


def _retry_after_seconds(value: Any) -> float | None:
    try:
        return max(0.0, min(30.0, float(value)))
    except (TypeError, ValueError):
        return None


def _compatible_payload_fallback(
    payload: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any] | None:
    if int(result.get("status_code") or 0) != 400:
        return None
    message = json.dumps(result.get("response"), ensure_ascii=False).casefold()
    unsupported = any(marker in message for marker in ("unsupported", "not supported", "unknown parameter", "unrecognized"))
    fallback = dict(payload)
    changed = False
    if "max_tokens" in fallback and "max_tokens" in message and (
        unsupported or "max_completion_tokens" in message
    ):
        fallback["max_completion_tokens"] = fallback.pop("max_tokens")
        changed = True
    if "temperature" in fallback and "temperature" in message and unsupported:
        fallback.pop("temperature", None)
        changed = True
    return fallback if changed else None
