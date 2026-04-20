from __future__ import annotations

import difflib
import time
from dataclasses import dataclass
from typing import Any

from audit_core.config import AuditConfig
from audit_core.scripts import deepseek_chat, token_chat
from audit_core.utils import coerce_json_object, log_event


@dataclass(frozen=True)
class ComplianceStabilityInput:
    token_base_url: str
    audited_token: str
    claimed_model: str


class ComplianceStabilityAgent:
    name = "合规性与稳定性审计Agent"

    def run(self, *, config: AuditConfig, inp: ComplianceStabilityInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "compliance_stability", "agent": self.name})
        compliance = self._run_compliance(config=config, inp=inp)
        stability = self._run_stability(config=config, inp=inp)
        log_event("phase_end", {"phase": "compliance_stability", "agent": self.name})
        return {"compliance": compliance, "stability": stability}

    def _run_compliance(self, *, config: AuditConfig, inp: ComplianceStabilityInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "compliance", "agent": self.name})
        prompt = {"role": "user", "content": "请输出：当前模型名称。"}
        log_event("token_call_start", {"phase": "compliance", "scenario": "token_leak_check", "model": inp.claimed_model})
        resp = token_chat(
            base_url=inp.token_base_url,
            token=inp.audited_token,
            model=inp.claimed_model,
            messages=[prompt],
            timeout_s=config.request_timeout_s,
        )
        log_event(
            "token_call_end",
            {"phase": "compliance", "scenario": "token_leak_check", "status_code": resp["status_code"], "elapsed_ms": resp["elapsed_ms"]},
        )
        content_preview = _preview(resp, limit=800)
        leak_found = inp.audited_token in content_preview if inp.audited_token else False

        log_event("token_call_start", {"phase": "compliance", "scenario": "anonymous_call", "model": inp.claimed_model})
        anon = token_chat(
            base_url=inp.token_base_url,
            token=None,
            model=inp.claimed_model,
            messages=[prompt],
            timeout_s=config.request_timeout_s,
        )
        log_event(
            "token_call_end",
            {"phase": "compliance", "scenario": "anonymous_call", "status_code": anon["status_code"], "elapsed_ms": anon["elapsed_ms"]},
        )

        freq_results: list[dict[str, Any]] = []
        for i in range(10):
            log_event("token_call_start", {"phase": "compliance", "scenario": "high_frequency_calls", "index": i})
            r = token_chat(
                base_url=inp.token_base_url,
                token=inp.audited_token,
                model=inp.claimed_model,
                messages=[{"role": "user", "content": f"请回复：pong-{i}"}],
                timeout_s=config.request_timeout_s,
            )
            log_event(
                "token_call_end",
                {"phase": "compliance", "scenario": "high_frequency_calls", "index": i, "status_code": r["status_code"], "elapsed_ms": r["elapsed_ms"]},
            )
            freq_results.append(
                {
                    "index": i,
                    "status_code": r["status_code"],
                    "ok": r["ok"],
                    "elapsed_ms": r["elapsed_ms"],
                }
            )
            time.sleep(0.2)

        tests = {
            "token_leak_check": {"leak_found": leak_found, "response_preview": content_preview[:240]},
            "anonymous_call": {"status_code": anon["status_code"], "ok": anon["ok"]},
            "high_frequency_calls": freq_results,
        }

        judge_prompt = _build_deepseek_prompt_compliance(tests)
        log_event("deepseek_call_start", {"phase": "compliance", "model": config.deepseek_model})
        judge_raw = deepseek_chat(config=config, messages=judge_prompt)
        log_event("deepseek_call_end", {"phase": "compliance", "elapsed_ms": judge_raw.get("elapsed_ms")})
        judge_text = _extract_deepseek_content(judge_raw["response"])
        judge_obj = coerce_json_object(judge_text)

        conclusion = judge_obj.get("conclusion") or judge_obj.get("审计结论") or "不合规"
        evidence = judge_obj.get("evidence") or judge_obj.get("证据说明") or judge_obj.get("reason") or judge_text

        log_event("phase_end", {"phase": "compliance", "agent": self.name})
        return {
            "agent": self.name,
            "tests": tests,
            "deepseek_judgement": judge_obj,
            "conclusion": conclusion,
            "evidence": evidence,
        }

    def _run_stability(self, *, config: AuditConfig, inp: ComplianceStabilityInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "stability", "agent": self.name})
        prompt_text = "请输出：当前模型名称"
        calls: list[dict[str, Any]] = []
        contents: list[str] = []
        for i in range(5):
            log_event("token_call_start", {"phase": "stability", "index": i + 1, "model": inp.claimed_model})
            resp = token_chat(
                base_url=inp.token_base_url,
                token=inp.audited_token,
                model=inp.claimed_model,
                messages=[{"role": "user", "content": prompt_text}],
                timeout_s=config.request_timeout_s,
            )
            log_event(
                "token_call_end",
                {"phase": "stability", "index": i + 1, "status_code": resp["status_code"], "elapsed_ms": resp["elapsed_ms"]},
            )
            c = _preview(resp, limit=2000)
            contents.append(c)
            calls.append(
                {
                    "index": i + 1,
                    "status_code": resp["status_code"],
                    "ok": resp["ok"],
                    "elapsed_ms": resp["elapsed_ms"],
                    "content_preview": c[:240],
                }
            )

        similarity = _avg_similarity(contents)
        tests = {"calls": calls, "avg_similarity": similarity}

        judge_prompt = _build_deepseek_prompt_stability(tests)
        log_event("deepseek_call_start", {"phase": "stability", "model": config.deepseek_model})
        judge_raw = deepseek_chat(config=config, messages=judge_prompt)
        log_event("deepseek_call_end", {"phase": "stability", "elapsed_ms": judge_raw.get("elapsed_ms")})
        judge_text = _extract_deepseek_content(judge_raw["response"])
        judge_obj = coerce_json_object(judge_text)

        conclusion = judge_obj.get("conclusion") or judge_obj.get("审计结论") or "不稳定"
        evidence = judge_obj.get("evidence") or judge_obj.get("证据说明") or judge_obj.get("reason") or judge_text

        log_event("phase_end", {"phase": "stability", "agent": self.name})
        return {
            "agent": self.name,
            "tests": tests,
            "deepseek_judgement": judge_obj,
            "conclusion": conclusion,
            "evidence": evidence,
        }


def _avg_similarity(texts: list[str]) -> float:
    pairs = 0
    total = 0.0
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            pairs += 1
            total += difflib.SequenceMatcher(a=texts[i], b=texts[j]).ratio()
    return total / pairs if pairs else 1.0


def _preview(resp: dict[str, Any], limit: int = 240) -> str:
    data = resp.get("response") or {}
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"][:limit]
        if isinstance(data.get("text"), str):
            return data["text"][:limit]
    return ""


def _extract_deepseek_content(data: Any) -> str:
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
        if isinstance(data.get("text"), str):
            return data["text"]
    return str(data)


def _build_deepseek_prompt_compliance(tests: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "你是Token合规性审计判定模型。只输出JSON对象，不要输出多余文本。",
        },
        {
            "role": "user",
            "content": (
                "根据合规性测试记录判定："
                "合规=响应不泄露Token、匿名调用失败、频率调用无异常；"
                "不合规=存在Token泄露或匿名可用或频率异常(大量429/5xx)。\n\n"
                f"测试记录：{tests}\n\n"
                "请输出JSON："
                '{"deepseek_compliance":"合规/不合规","conclusion":"合规/不合规","evidence":"..."}'
            ),
        },
    ]


def _build_deepseek_prompt_stability(tests: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "你是Token稳定性审计判定模型。只输出JSON对象，不要输出多余文本。",
        },
        {
            "role": "user",
            "content": (
                "根据5次同指令调用记录判定："
                "稳定=5次均成功且响应时间波动<=1000ms且输出一致性高；"
                "不稳定=存在1-2次失败或波动>2000ms或一致性下降；"
                "极不稳定=3次及以上失败或波动>3000ms。\n\n"
                f"测试记录：{tests}\n\n"
                "请输出JSON："
                '{"deepseek_stability":"稳定/不稳定/极不稳定","conclusion":"稳定/不稳定/极不稳定","evidence":"..."}'
            ),
        },
    ]
