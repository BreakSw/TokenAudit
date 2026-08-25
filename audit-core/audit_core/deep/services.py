from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
from threading import Lock
import time
from typing import Any

from audit_core.scripts.token_api import token_chat
from audit_core.utils import log_event


MAX_TARGET_OUTPUT_TOKENS = 99_999


class TargetTransportError(RuntimeError):
    pass


def execute_variants(
    *,
    base_url: str,
    token: str,
    model: str,
    round_index: int,
    groups: list[dict[str, Any]],
    timeout_s: float,
    concurrency: int = 3,
) -> list[dict[str, Any]]:
    jobs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for group in groups:
        for variant in group.get("variants", []):
            jobs.append((group, variant))
    recovery_lock = Lock()

    def run(group: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
        group_id = str(group.get("probe_group_id") or "unknown")
        variant_id = str(variant.get("variant_id") or "unknown")
        prompt_text = str(variant.get("prompt") or "")
        requested_max_tokens = max(
            512,
            min(MAX_TARGET_OUTPUT_TOKENS, int(group.get("max_tokens") or MAX_TARGET_OUTPUT_TOKENS)),
        )
        log_event(
            "deep_target_call_start",
            {
                "round": round_index,
                "probe_group_id": group_id,
                "variant_id": variant_id,
                "model": model,
                "max_tokens": requested_max_tokens,
                "prompt_preview": prompt_text[:800],
            },
        )
        current_max_tokens = requested_max_tokens
        retry_count = 0
        attempted_budgets: set[int] = set()
        best_result: dict[str, Any] | None = None
        best_response_text = ""
        best_max_tokens = requested_max_tokens
        result: dict[str, Any] = {}
        response_text = ""
        while len(attempted_budgets) < 3 and current_max_tokens not in attempted_budgets:
            attempted_budgets.add(current_max_tokens)
            result, transport_retries, used_budget = _request_target_with_recovery(
                base_url=base_url,
                token=token,
                model=model,
                prompt_text=prompt_text,
                timeout_s=timeout_s,
                max_tokens=current_max_tokens,
                recovery_lock=recovery_lock,
                event_context={
                    "round": round_index,
                    "probe_group_id": group_id,
                    "variant_id": variant_id,
                },
            )
            retry_count += transport_retries
            current_max_tokens = used_budget
            response_text = extract_response_text(result.get("response"))
            if result.get("ok") and (best_result is None or len(response_text.strip()) > len(best_response_text.strip())):
                best_result = result
                best_response_text = response_text
                best_max_tokens = current_max_tokens

            retry_reason = ""
            next_max_tokens: int | None = None
            affordable = _affordable_max_tokens(result.get("response")) if int(result.get("status_code") or 0) == 402 else None
            if affordable:
                candidate = max(512, min(MAX_TARGET_OUTPUT_TOKENS, int(affordable * 0.9)))
                if candidate < current_max_tokens:
                    retry_reason = "insufficient_credits_reduce_budget"
                    next_max_tokens = candidate
            elif result.get("ok") and _needs_final_content_retry(result.get("response"), response_text):
                candidate = min(
                    MAX_TARGET_OUTPUT_TOKENS,
                    max(current_max_tokens * 2, current_max_tokens + 4_000),
                )
                if candidate > current_max_tokens:
                    retry_reason = "empty_or_truncated_final_content"
                    next_max_tokens = candidate

            if next_max_tokens is None or next_max_tokens in attempted_budgets or len(attempted_budgets) >= 3:
                break
            retry_count += 1
            log_event(
                "deep_target_call_retry",
                {
                    "round": round_index,
                    "probe_group_id": group_id,
                    "variant_id": variant_id,
                    "reason": retry_reason,
                    "previous_max_tokens": current_max_tokens,
                    "max_tokens": next_max_tokens,
                    "affordable_max_tokens": affordable,
                },
            )
            current_max_tokens = next_max_tokens

        if best_result is not None:
            result = best_result
            response_text = best_response_text
            current_max_tokens = best_max_tokens
        error = ""
        if not result.get("ok"):
            error = safe_response_error(result.get("response"))
        elif not response_text.strip():
            error = "target_returned_no_final_content"
        output = {
            "round": round_index,
            "probe_group_id": group_id,
            "variant_id": variant_id,
            "variant_type": variant.get("variant_type"),
            "prompt": variant.get("prompt"),
            "ok": bool(result.get("ok")) and bool(response_text.strip()),
            "status_code": int(result.get("status_code") or 0),
            "elapsed_ms": int(result.get("elapsed_ms") or 0),
            "response_text": response_text,
            "error": error[:500],
            "retry_count": retry_count,
            "requested_max_tokens": requested_max_tokens,
            "used_max_tokens": current_max_tokens,
            "failure_kind": "" if bool(result.get("ok")) and bool(response_text.strip()) else _failure_kind(result),
        }
        log_event(
            "deep_target_call_end",
            {
                "round": round_index,
                "probe_group_id": group_id,
                "variant_id": variant_id,
                "status_code": output["status_code"],
                "elapsed_ms": output["elapsed_ms"],
                "ok": output["ok"],
                "response_chars": len(output["response_text"]),
                "response_preview": output["response_text"][:800],
                "retry_count": output["retry_count"],
                "requested_max_tokens": output["requested_max_tokens"],
                "used_max_tokens": output["used_max_tokens"],
                "error": output["error"],
            },
        )
        return output

    outputs: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, concurrency), thread_name_prefix="deep-target") as executor:
        futures = [executor.submit(run, group, variant) for group, variant in jobs]
        for future in as_completed(futures):
            outputs.append(future.result())
    outputs.sort(key=lambda item: (item["probe_group_id"], item["variant_id"]))
    return outputs


def _request_target_with_recovery(
    *,
    base_url: str,
    token: str,
    model: str,
    prompt_text: str,
    timeout_s: float,
    max_tokens: int,
    recovery_lock: Lock,
    event_context: dict[str, Any],
) -> tuple[dict[str, Any], int, int]:
    current_budget = max_tokens
    total_elapsed_ms = 0
    retries = 0
    initial_timeout = min(600.0, max(float(timeout_s), 120.0))
    result = token_chat(
        base_url=base_url,
        token=token,
        model=model,
        messages=[{"role": "user", "content": prompt_text}],
        timeout_s=initial_timeout,
        max_tokens=current_budget,
    )
    total_elapsed_ms += int(result.get("elapsed_ms") or 0)
    for attempt in range(1, 3):
        if not _is_transient_target_failure(result):
            break
        failure_kind = _failure_kind(result)
        if failure_kind == "timeout":
            current_budget = max(2_048, min(current_budget, 8_000))
        retry_timeout = min(600.0, initial_timeout + 60.0 * attempt)
        wait_seconds = float(result.get("retry_after_s") or min(2.0 * attempt, 4.0))
        retries += 1
        log_event(
            "deep_target_call_retry",
            {
                **event_context,
                "reason": f"transient_{failure_kind}",
                "attempt": attempt + 1,
                "max_tokens": current_budget,
                "timeout_s": retry_timeout,
                "recovery_concurrency": 1,
            },
        )
        # Only recovery calls are serialized. Normal calls keep the configured
        # parallelism, while rate-limited or fragile relays get a safe fallback.
        with recovery_lock:
            time.sleep(wait_seconds)
            result = token_chat(
                base_url=base_url,
                token=token,
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                timeout_s=retry_timeout,
                max_tokens=current_budget,
            )
        total_elapsed_ms += int(result.get("elapsed_ms") or 0)
    result = dict(result)
    result["elapsed_ms"] = total_elapsed_ms
    return result, retries, current_budget


def _is_transient_target_failure(result: dict[str, Any]) -> bool:
    if result.get("ok"):
        return False
    return int(result.get("status_code") or 0) in {0, 408, 425, 429, 500, 502, 503, 504}


def _failure_kind(result: dict[str, Any]) -> str:
    explicit = str(result.get("failure_kind") or "").strip().casefold()
    if explicit in {"timeout", "connection", "network", "protocol"}:
        return explicit
    status_code = int(result.get("status_code") or 0)
    if status_code in {408, 504}:
        return "timeout"
    if status_code in {425, 429, 500, 502, 503}:
        return "upstream"
    if status_code == 0:
        message = safe_response_error(result.get("response")).casefold()
        if "timed out" in message or "timeout" in message:
            return "timeout"
        return "connection"
    if status_code in {404, 405}:
        return "protocol"
    return "target"


def ensure_target_transport_integrity(
    responses: list[dict[str, Any]],
    *,
    max_transport_failure_ratio: float = 0.2,
) -> dict[str, Any]:
    total = len(responses)
    valid_responses = [item for item in responses if item.get("ok")]
    transport_failures = [
        item
        for item in responses
        if not item.get("ok") and item.get("failure_kind") in {"timeout", "connection", "network", "upstream"}
    ]
    ratio = len(transport_failures) / total if total else 1.0
    valid_ratio = len(valid_responses) / total if total else 0.0
    if not valid_responses:
        status = "failed"
    elif ratio > max_transport_failure_ratio or len(valid_responses) < total:
        status = "partial"
    else:
        status = "passed"
    summary = {
        "status": status,
        "responses": total,
        "valid_responses": len(valid_responses),
        "unscorable_responses": total - len(valid_responses),
        "valid_response_ratio": round(valid_ratio, 4),
        "transport_failures": len(transport_failures),
        "transport_failure_ratio": round(ratio, 4),
        "threshold": max_transport_failure_ratio,
        "failure_kinds": sorted({str(item.get("failure_kind")) for item in transport_failures}),
        "network_unstable": bool(transport_failures),
        "scoring_policy": "successful_responses_only",
    }
    log_event(
        "deep_target_transport_gate",
        summary,
    )
    if status == "failed":
        raise TargetTransportError(
            "target_returned_no_scorable_answers: "
            f"0/{total} requests returned a usable answer after retries"
        )
    return summary


def extract_response_text(response: Any) -> str:
    if not isinstance(response, dict):
        return ""
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        message = first.get("message") if isinstance(first, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str):
            return content
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    output = response.get("output")
    if isinstance(output, list):
        texts: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    texts.append(part["text"])
        return "\n".join(texts)
    return ""


def _needs_final_content_retry(response: Any, response_text: str) -> bool:
    if not response_text.strip():
        return True
    if not isinstance(response, dict):
        return False
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return False
    finish_reason = str(choices[0].get("finish_reason") or "").casefold()
    return finish_reason in {"length", "max_tokens", "token_limit"}


def safe_response_error(response: Any) -> str:
    if not isinstance(response, dict):
        return "target_request_failed"
    error = response.get("error")
    if isinstance(error, dict):
        return str(error.get("message") or error.get("code") or "target_request_failed")
    if error:
        return str(error)
    return str(response.get("message") or "target_request_failed")


def _affordable_max_tokens(response: Any) -> int | None:
    message = safe_response_error(response)
    match = re.search(r"can\s+only\s+afford\s+([\d,]+)", message, re.IGNORECASE)
    if not match:
        return None
    try:
        value = int(match.group(1).replace(",", ""))
    except ValueError:
        return None
    return value if value > 0 else None


def verify_objective_checks(groups: list[dict[str, Any]], responses: list[dict[str, Any]]) -> dict[str, Any]:
    grouped_responses: dict[str, list[dict[str, Any]]] = {}
    for response in responses:
        grouped_responses.setdefault(response["probe_group_id"], []).append(response)
    group_results: list[dict[str, Any]] = []
    for group in groups:
        group_id = str(group.get("probe_group_id"))
        checks = group.get("objective_checks") if isinstance(group.get("objective_checks"), list) else []
        all_variants = grouped_responses.get(group_id, [])
        variants = [variant for variant in all_variants if variant.get("ok")]
        variant_results = []
        for variant in variants:
            score, details = _verify_text(str(variant.get("response_text") or ""), checks, bool(variant.get("ok")))
            variant_results.append({"variant_id": variant["variant_id"], "score": score, "checks": details})
        scores = [item["score"] for item in variant_results]
        group_results.append(
            {
                "probe_group_id": group_id,
                "score": round(sum(scores) / len(scores), 2) if scores else 0.0,
                "scored_variants": len(variants),
                "unscorable_variants": len(all_variants) - len(variants),
                "variant_results": variant_results,
            }
        )
    scores = [item["score"] for item in group_results]
    return {"score": round(sum(scores) / len(scores), 2) if scores else 0.0, "groups": group_results}


def _verify_text(text: str, checks: list[dict[str, Any]], transport_ok: bool) -> tuple[float, list[dict[str, Any]]]:
    if not transport_ok or not text.strip():
        return 0.0, [{"type": "transport", "passed": False}]
    supported_results: list[dict[str, Any]] = []
    for check in checks:
        kind = str(check.get("type") or "").casefold()
        passed: bool | None = None
        if kind == "min_length":
            passed = len(text) >= int(check.get("value") or 1)
        elif kind == "max_length":
            passed = len(text) <= int(check.get("value") or 100000)
        elif kind == "contains_any":
            values = [str(item).casefold() for item in check.get("values", [])]
            passed = bool(values) and any(value in text.casefold() for value in values)
        elif kind == "contains_all":
            values = [str(item).casefold() for item in check.get("values", [])]
            passed = bool(values) and all(value in text.casefold() for value in values)
        elif kind == "not_contains":
            values = [str(item).casefold() for item in check.get("values", [])]
            passed = all(value not in text.casefold() for value in values)
        elif kind == "json_keys":
            try:
                parsed = json.loads(_extract_json(text))
                values = [str(item) for item in check.get("values", [])]
                passed = isinstance(parsed, dict) and all(value in parsed for value in values)
            except Exception:
                passed = False
        elif kind == "regex":
            try:
                passed = re.search(str(check.get("value") or ""), text) is not None
            except re.error:
                passed = None
        if passed is not None:
            supported_results.append({"type": kind, "passed": passed})
    if not supported_results:
        return 50.0, [{"type": "nonempty_response", "passed": True, "neutral": True}]
    score = 100.0 * sum(1 for result in supported_results if result["passed"]) / len(supported_results)
    return round(score, 2), supported_results


def _extract_json(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.I)
    if fenced:
        return fenced.group(1)
    start = min((index for index in (text.find("{"), text.find("[")) if index >= 0), default=-1)
    if start < 0:
        return text
    closing = "}" if text[start] == "{" else "]"
    end = text.rfind(closing)
    return text[start : end + 1] if end > start else text


def fuse_scores(rounds: list[dict[str, Any]], *, coverage: float) -> dict[str, Any]:
    objective = _mean(round_item.get("objective", {}).get("score") for round_item in rounds)
    semantic = _mean(round_item.get("audit_judgement", {}).get("semantic_score") for round_item in rounds)
    official = _mean(round_item.get("audit_judgement", {}).get("ground_truth_alignment_score") for round_item in rounds)
    behavior = _mean(round_item.get("behavior_judgement", {}).get("behavior_score") for round_item in rounds)
    consistency = _mean(round_item.get("consistency_judgement", {}).get("consistency_score") for round_item in rounds)
    weighted = (
        objective * 0.10
        + semantic * 0.30
        + official * 0.25
        + behavior * 0.20
        + consistency * 0.15
    )
    valid_responses = sum(1 for item in rounds for response in item.get("responses", []) if response.get("ok"))
    total_responses = sum(len(item.get("responses", [])) for item in rounds)
    network_failures = sum(
        1
        for item in rounds
        for response in item.get("responses", [])
        if not response.get("ok") and response.get("failure_kind") in {"timeout", "connection", "network", "upstream"}
    )
    valid_ratio = valid_responses / total_responses if total_responses else 0.0
    confidence = max(0.0, min(1.0, coverage * valid_ratio * min(1.0, 0.55 + 0.15 * len(rounds))))
    if weighted >= 80:
        band = "highly_consistent"
    elif weighted >= 65:
        band = "partially_consistent"
    elif weighted >= 50:
        band = "suspicious"
    else:
        band = "strong_mismatch"
    return {
        "total_score": round(weighted, 2),
        "band": band,
        "confidence": round(confidence, 4),
        "valid_response_ratio": round(valid_ratio, 4),
        "scored_responses": valid_responses,
        "total_responses": total_responses,
        "network_failures": network_failures,
        "network_unstable": network_failures > 0,
        "scoring_policy": "successful_responses_only",
        "components": {
            "objective": round(objective, 2),
            "semantic": round(semantic, 2),
            "official_ground_truth": round(official, 2),
            "behavior_differential": round(behavior, 2),
            "fuzz_consistency": round(consistency, 2),
        },
        "weights": {
            "objective": 0.10,
            "semantic": 0.30,
            "official_ground_truth": 0.25,
            "behavior_differential": 0.20,
            "fuzz_consistency": 0.15,
        },
    }


def _mean(values: Any) -> float:
    numbers = [float(value) for value in values if isinstance(value, (int, float))]
    return sum(numbers) / len(numbers) if numbers else 0.0
