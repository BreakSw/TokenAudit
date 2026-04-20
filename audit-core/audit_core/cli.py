from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from typing import Any

from audit_core.agents import OrchestratorAgent
from audit_core.agents.orchestrator_agent import OrchestratorInput
from audit_core.config import load_config
from audit_core.scripts.report_generate import default_basename, export_excel, export_pdf, write_report_json, write_report_markdown


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
        non_claimed_model=str(inp_obj.get("non_claimed_model") or "gpt-4o-mini"),
        audit_time=audit_time,
        audit_dimensions=inp_obj.get("audit_dimensions"),
        front_end_url=inp_obj.get("front_end_url"),
        back_end_url=inp_obj.get("back_end_url"),
    )

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
