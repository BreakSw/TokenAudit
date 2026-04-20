from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from audit_core.config import AuditConfig
from audit_core.scripts import deepseek_chat, token_chat
from audit_core.scripts.token_api import token_models
from audit_core.utils import coerce_json_object, log_event


@dataclass(frozen=True)
class ValidityInput:
    token_base_url: str
    audited_token: str
    claimed_model: str


class ValidityAgent:
    name = "有效性审计Agent"

    def run(self, *, config: AuditConfig, inp: ValidityInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "validity", "agent": self.name})
        models_probe = token_models(base_url=inp.token_base_url, token=inp.audited_token, timeout_s=min(20, config.request_timeout_s))
        model_listed = _model_in_list(models_probe.get("response"), inp.claimed_model)
        log_event(
            "token_models",
            {
                "phase": "validity",
                "status_code": models_probe.get("status_code"),
                "elapsed_ms": models_probe.get("elapsed_ms"),
                "ok": models_probe.get("ok"),
                "model_listed": model_listed,
                "endpoint": models_probe.get("endpoint"),
            },
        )
        prompts = [
            {"role": "user", "content": "请回复：OK"},
            {"role": "user", "content": "请用Python写一个快速排序函数，并给出一个简单示例。"},
            {
                "role": "user",
                "content": "请用不少于400字说明：如何设计一个Token审计系统的后端接口与数据模型？",
            },
        ]
        tests: list[dict[str, Any]] = []
        for i, msg in enumerate(prompts, start=1):
            log_event("token_call_start", {"phase": "validity", "index": i, "model": inp.claimed_model})
            resp = token_chat(
                base_url=inp.token_base_url,
                token=inp.audited_token,
                model=inp.claimed_model,
                messages=[msg],
                timeout_s=config.request_timeout_s,
            )
            log_event(
                "token_call_end",
                {
                    "phase": "validity",
                    "index": i,
                    "status_code": resp["status_code"],
                    "elapsed_ms": resp["elapsed_ms"],
                    "endpoint": resp.get("endpoint"),
                    "url": resp.get("url"),
                },
            )
            tests.append(
                {
                    "index": i,
                    "prompt": msg["content"],
                    "status_code": resp["status_code"],
                    "elapsed_ms": resp["elapsed_ms"],
                    "ok": resp["ok"],
                    "endpoint": resp.get("endpoint"),
                    "url": resp.get("url"),
                    "response_preview": _preview(resp),
                }
            )

        if tests and all(t.get("status_code") in (0, 503) for t in tests):
            judge_obj = {
                "deepseek_validity": "异常",
                "conclusion": "模型不可用",
                "evidence": {
                    "reason": "all_calls_failed",
                    "hint": "通常为模型名不支持/未开通、组/配额限制、上游不可用或中转站熔断",
                    "model": inp.claimed_model,
                    "model_listed": model_listed,
                    "models_probe": {
                        "status_code": models_probe.get("status_code"),
                        "ok": models_probe.get("ok"),
                        "elapsed_ms": models_probe.get("elapsed_ms"),
                        "response_preview": _preview(models_probe),
                    },
                    "status_codes": [t.get("status_code") for t in tests],
                },
            }
            log_event("phase_end", {"phase": "validity", "agent": self.name})
            return {
                "agent": self.name,
                "tests": tests,
                "deepseek_judgement": judge_obj,
                "conclusion": judge_obj["conclusion"],
                "evidence": judge_obj["evidence"],
            }

        judge_prompt = _build_deepseek_prompt(tests)
        log_event("deepseek_call_start", {"phase": "validity", "model": config.deepseek_model})
        judge_raw = deepseek_chat(config=config, messages=judge_prompt)
        log_event("deepseek_call_end", {"phase": "validity", "elapsed_ms": judge_raw.get("elapsed_ms")})
        judge_text = _extract_deepseek_content(judge_raw["response"])
        judge_obj = coerce_json_object(judge_text)

        conclusion = judge_obj.get("conclusion") or judge_obj.get("审计结论") or judge_obj.get("result") or "异常"
        evidence = judge_obj.get("evidence") or judge_obj.get("证据说明") or judge_obj.get("reason") or judge_text

        log_event("phase_end", {"phase": "validity", "agent": self.name})
        return {
            "agent": self.name,
            "tests": tests,
            "deepseek_judgement": judge_obj,
            "conclusion": conclusion,
            "evidence": evidence,
        }


def _preview(resp: dict[str, Any], limit: int = 240) -> str:
    data = resp.get("response") or {}
    if isinstance(data, dict):
        err = data.get("error")
        if isinstance(err, dict) and isinstance(err.get("message"), str) and err.get("message"):
            return err["message"][:limit]
        if isinstance(err, str) and err:
            return err[:limit]
        if isinstance(data.get("message"), str) and data.get("message"):
            return data["message"][:limit]
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"][:limit]
        if isinstance(data.get("text"), str):
            return data["text"][:limit]
    return ""


def _model_in_list(models_response: Any, model: str) -> bool:
    if not model:
        return False
    m = model.strip()
    if not m:
        return False
    if isinstance(models_response, dict):
        data = models_response.get("data")
        if isinstance(data, list):
            for it in data:
                if isinstance(it, dict) and it.get("id") == m:
                    return True
    return False


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


def _build_deepseek_prompt(tests: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "你是Token有效性审计判定模型。只输出JSON对象，不要输出多余文本。",
        },
        {
            "role": "user",
            "content": (
                "根据以下3次调用测试记录，判定Token有效性。判定标准："
                "有效=3次均200且响应时间<=3000ms且无过期/封禁提示；"
                "无效=401/403/500等或明确过期/封禁；"
                "异常=部分成功部分失败或响应时间波动大(>5000ms)。\n\n"
                f"测试记录：{tests}\n\n"
                "请输出JSON："
                '{"deepseek_validity":"有效/无效/异常","conclusion":"有效/无效/异常","evidence":"..."}'
            ),
        },
    ]
