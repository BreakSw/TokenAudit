from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Any

from audit_core.agents import OrchestratorAgent
from audit_core.agents.orchestrator_agent import OrchestratorInput
from audit_core.config import load_config
from audit_core.deep import DeepAuditOrchestrator, DeepAuditSettings
from audit_core.scripts.audit_ai_preflight import run_audit_ai_preflight
from audit_core.scripts.relay_preflight import run_relay_preflight
from audit_core.scripts.report_generate import default_basename, export_excel, export_pdf, write_report_json, write_report_markdown
from audit_core.utils import log_event


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        sys.stdout.write(json.dumps({"error": "empty input"}, ensure_ascii=False))
        return 2

    inp_obj = json.loads(raw)
    config = load_config()
    audit_time = inp_obj.get("audit_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    orch_inp = OrchestratorInput(
        token_id=inp_obj.get("token_id"),
        audited_token=str(inp_obj.get("audited_token") or ""),
        platform=str(inp_obj.get("platform") or ""),
        token_base_url=str(inp_obj.get("token_base_url") or ""),
        claimed_model=str(inp_obj.get("claimed_model") or ""),
        non_claimed_model=str(inp_obj.get("non_claimed_model") or "").strip(),
        audit_time=audit_time,
        audit_dimensions=inp_obj.get("audit_dimensions"),
        front_end_url=inp_obj.get("front_end_url"),
        back_end_url=inp_obj.get("back_end_url"),
    )

    preflight = run_relay_preflight(
        base_url=orch_inp.token_base_url,
        token=orch_inp.audited_token,
        model=orch_inp.claimed_model,
        timeout_s=config.request_timeout_s,
    )
    if not preflight["passed"]:
        error_payload = {
            "phase": "preflight",
            "reason": preflight["reason"],
            "status_code": preflight["status_code"],
            "message": preflight["message"],
            "model": preflight["model"],
        }
        log_event("audit_aborted", error_payload)
        sys.stderr.write("relay_preflight_failed:" + json.dumps(error_payload, ensure_ascii=False) + "\n")
        sys.stderr.flush()
        return 3

    audit_ai_preflight = run_audit_ai_preflight(config=config)
    if not audit_ai_preflight["passed"]:
        error_payload = {
            "phase": "audit_ai_preflight",
            "reason": audit_ai_preflight["reason"],
            "status_code": audit_ai_preflight["status_code"],
            "message": audit_ai_preflight["message"],
            "model": audit_ai_preflight["model"],
            "endpoint": audit_ai_preflight["endpoint"],
            "url": audit_ai_preflight["url"],
        }
        log_event("audit_aborted", error_payload)
        sys.stderr.write("audit_ai_preflight_failed:" + json.dumps(error_payload, ensure_ascii=False) + "\n")
        sys.stderr.flush()
        return 4

    audit_mode = str(inp_obj.get("audit_mode") or "quick").strip().casefold()
    if audit_mode == "deep":
        report = DeepAuditOrchestrator().run(
            config=config,
            inp=orch_inp,
            settings=DeepAuditSettings(
                rounds=int(inp_obj.get("deep_audit_rounds") or 2),
                questions_per_round=3,
                variants_per_question=3,
                target_concurrency=int(inp_obj.get("deep_target_concurrency") or 3),
                adaptive_early_stop=bool(inp_obj.get("adaptive_early_stop", False)),
            ),
        )
    else:
        report = OrchestratorAgent().run(config=config, inp=orch_inp)

    export_formats = inp_obj.get("export_formats") or []
    if isinstance(export_formats, str):
        export_formats = [export_formats]
    export_formats = [str(x).lower() for x in export_formats]

    basename = default_basename()
    out_dir = config.export_dir
    file_outputs: dict[str, Any] = {}
    export_errors: dict[str, Any] = {}

    if "json" in export_formats:
        try:
            file_outputs["json"] = write_report_json(report=report, out_dir=out_dir, basename=basename)
        except Exception as e:
            export_errors["json"] = str(e)
    if "md" in export_formats:
        try:
            file_outputs["md"] = write_report_markdown(
                report_markdown=report.get("report_markdown") or "",
                out_dir=out_dir,
                basename=basename,
            )
        except Exception as e:
            export_errors["md"] = str(e)
    if "xlsx" in export_formats or "excel" in export_formats:
        try:
            file_outputs["xlsx"] = export_excel(report=report, out_dir=out_dir, basename=basename)
        except Exception as e:
            export_errors["xlsx"] = str(e)
    if "pdf" in export_formats:
        try:
            file_outputs["pdf"] = export_pdf(
                report_markdown=report.get("report_markdown") or "",
                out_dir=out_dir,
                basename=basename,
            )
        except Exception as e:
            export_errors["pdf"] = str(e)

    report["exports"] = file_outputs
    if export_errors:
        report["export_errors"] = export_errors
    sys.stdout.write(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
