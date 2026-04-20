from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from audit_core.utils import log_agent_result, log_event


@dataclass(frozen=True)
class SummaryInput:
    token_id: int | None
    audit_time: str
    agent_results: list[dict[str, Any]]


class SummaryAgent:
    name = "SummaryAgent"

    def run(self, *, inp: SummaryInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "summary", "agent": self.name})
        audit_time = inp.audit_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_id = f"report_{inp.token_id or 0}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        dimension_summary: list[dict[str, Any]] = []
        risks: list[str] = []
        suggestions: list[str] = []

        statuses: list[str] = []
        for r in inp.agent_results:
            dim = r.get("audit_dimension") or ""
            status = r.get("status") or "error"
            statuses.append(status)
            core_result = r.get("result")
            dimension_summary.append({"audit_dimension": dim, "status": status, "core_result": core_result})
            if status in ("fail", "error"):
                msg = r.get("error_msg") or ""
                if msg:
                    risks.append(f"{dim}:{msg}")

            ev = r.get("result") or {}
            if isinstance(ev, dict):
                sug = ev.get("reinforcement_suggestion") or ev.get("rectify_suggestion") or ev.get("clean_suggestion")
                if isinstance(sug, str) and sug:
                    suggestions.append(sug)

        overall_status = "pass"
        if any(s == "error" for s in statuses):
            overall_status = "error"
        elif any(s == "fail" for s in statuses) and any(s == "success" for s in statuses):
            overall_status = "partial_pass"
        elif any(s == "fail" for s in statuses):
            overall_status = "fail"

        out = {
            "agent_name": self.name,
            "audit_time": audit_time,
            "token_id": inp.token_id,
            "overall_status": overall_status,
            "dimension_summary": dimension_summary,
            "risk_summary": "；".join(risks),
            "optimization_suggestion": "；".join(suggestions),
            "error_msg": "",
            "report_id": report_id,
        }
        log_agent_result(out)
        log_event("phase_end", {"phase": "summary", "agent": self.name})
        return out

