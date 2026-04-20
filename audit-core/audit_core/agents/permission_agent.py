from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from audit_core.config import AuditConfig
from audit_core.scripts import deepseek_chat, token_chat
from audit_core.utils import coerce_json_object, log_event


@dataclass(frozen=True)
class PermissionInput:
    token_base_url: str
    audited_token: str
    claimed_model: str
    non_claimed_model: str


class PermissionAgent:
    name = "权限审计Agent"

    def run(self, *, config: AuditConfig, inp: PermissionInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "permission", "agent": self.name})
        prompt = {"role": "user", "content": "请直接输出：当前模型名称，并简要说明你是否支持函数调用。"}

        log_event("token_call_start", {"phase": "permission", "scenario": "claimed_model", "model": inp.claimed_model})
        claimed = token_chat(
            base_url=inp.token_base_url,
            token=inp.audited_token,
            model=inp.claimed_model,
            messages=[prompt],
            timeout_s=config.request_timeout_s,
        )
        log_event(
            "token_call_end",
            {
                "phase": "permission",
                "scenario": "claimed_model",
                "status_code": claimed["status_code"],
                "elapsed_ms": claimed["elapsed_ms"],
                "endpoint": claimed.get("endpoint"),
                "url": claimed.get("url"),
            },
        )

        log_event("token_call_start", {"phase": "permission", "scenario": "non_claimed_model", "model": inp.non_claimed_model})
        non_claimed = token_chat(
            base_url=inp.token_base_url,
            token=inp.audited_token,
            model=inp.non_claimed_model,
            messages=[prompt],
            timeout_s=config.request_timeout_s,
        )
        log_event(
            "token_call_end",
            {
                "phase": "permission",
                "scenario": "non_claimed_model",
                "status_code": non_claimed["status_code"],
                "elapsed_ms": non_claimed["elapsed_ms"],
                "endpoint": non_claimed.get("endpoint"),
                "url": non_claimed.get("url"),
            },
        )

        log_event("token_call_start", {"phase": "permission", "scenario": "anonymous_call", "model": inp.claimed_model})
        anonymous = token_chat(
            base_url=inp.token_base_url,
            token=None,
            model=inp.claimed_model,
            messages=[prompt],
            timeout_s=config.request_timeout_s,
        )
        log_event(
            "token_call_end",
            {
                "phase": "permission",
                "scenario": "anonymous_call",
                "status_code": anonymous["status_code"],
                "elapsed_ms": anonymous["elapsed_ms"],
                "endpoint": anonymous.get("endpoint"),
                "url": anonymous.get("url"),
            },
        )

        tests = [
            {
                "scenario": "claimed_model",
                "model": inp.claimed_model,
                "status_code": claimed["status_code"],
                "ok": claimed["ok"],
                "elapsed_ms": claimed["elapsed_ms"],
                "endpoint": claimed.get("endpoint"),
                "url": claimed.get("url"),
                "response_preview": _preview(claimed),
            },
            {
                "scenario": "non_claimed_model",
                "model": inp.non_claimed_model,
                "status_code": non_claimed["status_code"],
                "ok": non_claimed["ok"],
                "elapsed_ms": non_claimed["elapsed_ms"],
                "endpoint": non_claimed.get("endpoint"),
                "url": non_claimed.get("url"),
                "response_preview": _preview(non_claimed),
            },
            {
                "scenario": "anonymous_call",
                "model": inp.claimed_model,
                "status_code": anonymous["status_code"],
                "ok": anonymous["ok"],
                "elapsed_ms": anonymous["elapsed_ms"],
                "endpoint": anonymous.get("endpoint"),
                "url": anonymous.get("url"),
                "response_preview": _preview(anonymous),
            },
        ]

        judge_prompt = _build_deepseek_prompt(inp=inp, tests=tests)
        log_event("deepseek_call_start", {"phase": "permission", "model": config.deepseek_model})
        judge_raw = deepseek_chat(config=config, messages=judge_prompt)
        log_event("deepseek_call_end", {"phase": "permission", "elapsed_ms": judge_raw.get("elapsed_ms")})
        judge_text = _extract_deepseek_content(judge_raw["response"])
        judge_obj = coerce_json_object(judge_text)

        conclusion = (
            judge_obj.get("conclusion")
            or judge_obj.get("审计结论")
            or judge_obj.get("result")
            or "权限异常"
        )
        evidence = judge_obj.get("evidence") or judge_obj.get("证据说明") or judge_obj.get("reason") or judge_text

        log_event("phase_end", {"phase": "permission", "agent": self.name})
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


def _build_deepseek_prompt(*, inp: PermissionInput, tests: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "你是Token权限审计判定模型。只输出JSON对象，不要输出多余文本。",
        },
        {
            "role": "user",
            "content": (
                "根据以下权限测试记录判定："
                "权限正常=仅能调用宣称模型且匿名调用失败；"
                "权限异常=可调用未宣称模型或无法调用宣称模型；"
                "匿名权限异常=匿名调用成功。\n\n"
                f"宣称模型={inp.claimed_model}，非宣称模型={inp.non_claimed_model}\n"
                f"测试记录：{tests}\n\n"
                "请输出JSON："
                '{"deepseek_permission":"权限正常/权限异常/匿名权限异常","conclusion":"权限正常/权限异常/匿名权限异常","evidence":"..."}'
            ),
        },
    ]
