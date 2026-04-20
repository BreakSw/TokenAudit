from __future__ import annotations

import json
import re
from typing import Any


def safe_json_loads(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_json_candidate(text: str) -> str | None:
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()
    return None


def coerce_json_object(text: str) -> dict[str, Any]:
    parsed = safe_json_loads(text)
    if isinstance(parsed, dict):
        return parsed

    candidate = _extract_json_candidate(text)
    if candidate:
        parsed2 = safe_json_loads(candidate)
        if isinstance(parsed2, dict):
            return parsed2

    return {"raw_text": text}
