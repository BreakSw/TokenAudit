from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from audit_core.config import AuditConfig
from audit_core.scripts import deepseek_chat, token_chat
from audit_core.scripts.feature_extract import extract_features
from audit_core.utils import coerce_json_object, log_event


@dataclass(frozen=True)
class WateringInput:
    token_base_url: str
    audited_token: str
    claimed_model: str


class WateringAgent:
    name = "掺水审计Agent"

    def run(self, *, config: AuditConfig, inp: WateringInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "watering", "agent": self.name})
        prompts = [
            {"role": "user", "content": "请直接输出：你当前的模型全名。"},
            {"role": "user", "content": "请解答：给定n=10，计算1到n的立方和，并给出推导过程。"},
            {
                "role": "user",
                "content": "请回答：你训练数据的知识截止日期大致到什么时候？如果不确定，请说明不确定。",
            },
        ]
        calls: list[dict[str, Any]] = []
        for i, msg in enumerate(prompts, start=1):
            log_event("token_call_start", {"phase": "watering", "index": i, "model": inp.claimed_model})
            resp = token_chat(
                base_url=inp.token_base_url,
                token=inp.audited_token,
                model=inp.claimed_model,
                messages=[msg],
                timeout_s=config.request_timeout_s,
            )
            log_event(
                "token_call_end",
                {"phase": "watering", "index": i, "status_code": resp["status_code"], "elapsed_ms": resp["elapsed_ms"]},
            )
            feat = extract_features(resp).to_dict()
            calls.append(
                {
                    "index": i,
                    "prompt": msg["content"],
                    "status_code": resp["status_code"],
                    "elapsed_ms": resp["elapsed_ms"],
                    "ok": resp["ok"],
                    "response_preview": _preview(resp),
                    "features": feat,
                }
            )

        judge_prompt = _build_deepseek_prompt(inp=inp, calls=calls)
        log_event("deepseek_call_start", {"phase": "watering", "model": config.deepseek_model})
        judge_raw = deepseek_chat(config=config, messages=judge_prompt)
        log_event("deepseek_call_end", {"phase": "watering", "elapsed_ms": judge_raw.get("elapsed_ms")})
        judge_text = _extract_deepseek_content(judge_raw["response"])
        judge_obj = coerce_json_object(judge_text)

        conclusion = judge_obj.get("conclusion") or judge_obj.get("审计结论") or "疑似掺水"
        evidence = judge_obj.get("evidence") or judge_obj.get("证据说明") or judge_obj.get("reason") or judge_text

        log_event("phase_end", {"phase": "watering", "agent": self.name})
        return {
            "agent": self.name,
            "tests": calls,
            "deepseek_judgement": judge_obj,
            "conclusion": conclusion,
            "evidence": evidence,
        }


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


def _build_deepseek_prompt(*, inp: WateringInput, calls: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "你是Token掺水审计判定模型。只输出JSON对象，不要输出多余文本。",
        },
        {
            "role": "user",
            "content": (
                "根据以下多轮调用的响应特征，判断是否存在掺水/降级/套皮。"
                "无掺水=整体特征稳定且符合宣称模型能力；"
                "疑似掺水=特征波动或能力不稳定；"
                "确认掺水=多轮明显低等级能力/自报模型与宣称不符。\n\n"
                f"宣称模型={inp.claimed_model}\n"
                f"测试记录：{calls}\n\n"
                "请输出JSON："
                '{"deepseek_watering":"无掺水/疑似掺水/确认掺水","conclusion":"无掺水/疑似掺水/确认掺水","evidence":"..."}'
            ),
        },
    ]
