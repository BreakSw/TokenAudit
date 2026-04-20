from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from audit_core.config import AuditConfig
from audit_core.scripts import token_chat
from audit_core.utils import log_event
from audit_core.utils.security_util import detect_basic_risks


@dataclass(frozen=True)
class SecurityInput:
    token_id: int | None
    token_value: str
    token_base_url: str
    claimed_model: str
    audit_time: str


class SecurityAgent:
    name = "安全审计Agent"

    def run(self, *, config: AuditConfig, inp: SecurityInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "security", "agent": self.name})
        audit_time = inp.audit_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        checks: list[dict[str, Any]] = []
        base = detect_basic_risks(inp.token_value)
        checks.append({"type": "static_checks", **base})

        log_event("token_call_start", {"phase": "security", "scenario": "anonymous_call", "model": inp.claimed_model})
        anon = token_chat(
            base_url=inp.token_base_url,
            token=None,
            model=inp.claimed_model,
            messages=[{"role": "user", "content": "ping"}],
            timeout_s=min(config.request_timeout_s, 20),
        )
        log_event(
            "token_call_end",
            {"phase": "security", "scenario": "anonymous_call", "status_code": anon["status_code"], "elapsed_ms": anon["elapsed_ms"]},
        )
        if anon.get("ok"):
            base["security_hidden_dangers"].append("匿名调用可成功返回，存在未授权访问风险")
            base["risk_level"] = "high"
            base["reinforcement_suggestion"] = "建议强制鉴权（禁止匿名调用），开启限流与白名单，并定期轮换Token。"
        checks.append({"type": "anonymous_call", "status_code": anon.get("status_code"), "ok": anon.get("ok")})

        conclusion = "低风险"
        if base["risk_level"] == "middle":
            conclusion = "中风险"
        if base["risk_level"] == "high":
            conclusion = "高风险"

        log_event("phase_end", {"phase": "security", "agent": self.name})
        return {
            "agent": self.name,
            "audit_time": audit_time,
            "tests": checks,
            "deepseek_judgement": None,
            "conclusion": conclusion,
            "evidence": base,
        }

