from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any


def log_event(event: str, payload: dict[str, Any] | None = None) -> None:
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": payload or {},
    }
    sys.stderr.write(json.dumps(record, ensure_ascii=False) + "\n")
    sys.stderr.flush()


def log_agent_result(record: dict[str, Any]) -> None:
    path = os.getenv("AUDIT_AGENT_LOG_PATH") or os.getenv("AUDIT_LOG_PATH")
    if not path:
        path = os.path.abspath(os.path.join(os.getcwd(), "..", "data", "logs", "agent_audit.jsonl"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
