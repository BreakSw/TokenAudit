from __future__ import annotations

import json
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
