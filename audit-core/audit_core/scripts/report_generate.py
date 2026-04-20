from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import pandas as pd


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_report_json(*, report: dict[str, Any], out_dir: str, basename: str) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"{basename}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path


def write_report_markdown(*, report_markdown: str, out_dir: str, basename: str) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"{basename}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_markdown)
    return path


def export_excel(*, report: dict[str, Any], out_dir: str, basename: str) -> str | None:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"{basename}.xlsx")

    rows: list[dict[str, Any]] = []
    base = report.get("base_info") or {}
    for section_key in ["validity", "permission", "watering", "compliance", "stability", "security"]:
        section = report.get("sections", {}).get(section_key) or {}
        rows.append(
            {
                "section": section_key,
                "conclusion": section.get("conclusion"),
                "deepseek_judgement": section.get("deepseek_judgement"),
                "evidence": section.get("evidence"),
                "agent": section.get("agent"),
            }
        )
    df_summary = pd.DataFrame(rows)
    df_base = pd.DataFrame(
        [
            {
                "token": base.get("token_masked"),
                "platform": base.get("platform"),
                "claimed_model": base.get("claimed_model"),
                "audit_time": base.get("audit_time"),
            }
        ]
    )

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df_base.to_excel(writer, sheet_name="base", index=False)
        df_summary.to_excel(writer, sheet_name="summary", index=False)
    return path


def export_pdf(*, report_markdown: str, out_dir: str, basename: str) -> str | None:
    try:
        from fpdf import FPDF
    except Exception:
        return None

    ensure_dir(out_dir)
    path = os.path.join(out_dir, f"{basename}.pdf")
    font_ttf = os.getenv("AUDIT_PDF_FONT_TTF")
    if not font_ttf:
        try:
            report_markdown.encode("latin-1")
        except Exception:
            return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    if font_ttf:
        pdf.add_font("AuditFont", "", font_ttf, uni=True)
        pdf.set_font("AuditFont", size=11)
    else:
        pdf.set_font("Helvetica", size=11)

    for line in report_markdown.splitlines():
        pdf.multi_cell(0, 6, line)

    pdf.output(path)
    return path


def default_basename(prefix: str = "token_audit") -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}"
