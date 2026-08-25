from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

import pyarrow.parquet as pq


SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"Bearer\s+[A-Za-z0-9._~-]{24,}", re.IGNORECASE),
)


def iter_rows(path: Path) -> Iterable[dict[str, Any]]:
    if path.suffix == ".jsonl":
        with path.open(encoding="utf-8") as source:
            for line in source:
                if line.strip():
                    yield json.loads(line)
        return
    if path.suffix == ".parquet":
        yield from pq.read_table(path).to_pylist()
        return
    raise ValueError(f"Unsupported dataset file: {path}")


def canonical_hash(row: dict[str, Any]) -> str:
    payload = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the compact TokenAudit HF set")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    checks: dict[str, Any] = {}
    total_bytes = sum(path.stat().st_size for path in root.rglob("*") if path.is_file())

    for model in manifest["models"]:
        model_id = model["model_id"]
        if not model["output"]:
            checks[model_id] = {"rows": 0, "status": "no-public-data"}
            continue
        path = root / model["output"]
        rows = list(iter_rows(path))
        hashes = [canonical_hash(row) for row in rows]
        serialized = [
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows
        ]
        secret_pattern_matches = sum(
            bool(pattern.search(text)) for text in serialized for pattern in SECRET_PATTERNS
        )
        result: dict[str, Any] = {
            "rows": len(rows),
            "manifest_rows_match": len(rows) == model["rows"],
            "exact_duplicate_rows": len(rows) - len(set(hashes)),
            "secret_pattern_matches": secret_pattern_matches,
        }
        if model_id == "claude-fable-5":
            result["source_sessions"] = len({row.get("session") for row in rows})
            result["model_field_valid"] = all(
                row.get("model") == "claude-fable-5" for row in rows
            )
        elif model_id == "deepseek-v4-pro":
            result["unique_sessions"] = len({row.get("session_id") for row in rows})
        elif model_id == "glm-5.2":
            result["source_files"] = len(
                {row.get("tokenaudit_source_file") for row in rows}
            )
            result["outcomes"] = sorted(
                {row.get("tokenaudit_benchmark_outcome") for row in rows}
            )
        elif model_id == "gpt-5.6-luna":
            result["model_field_valid"] = all(
                row.get("model") == "openai/gpt-5.6-luna" for row in rows
            )
        elif model_id == "gpt-5.6-sol":
            result["unique_trajectories"] = len(
                {row.get("source_trajectory_id") for row in rows}
            )
            result["categories"] = len({row.get("category") for row in rows})
            result["model_field_valid"] = all(
                row.get("teacher_model") == "gpt-5.6-sol" for row in rows
            )
            result["all_final_steps"] = all(
                row.get("assistant_step") == row.get("assistant_steps") for row in rows
            )
        elif model_id == "kimi-k3":
            result["unique_trajectories"] = len(
                {row.get("source_trajectory_id") for row in rows}
            )
            result["observed_model_valid"] = all(
                "moonshotai/kimi-k3" in (row.get("observed_models") or [])
                for row in rows
            )
        checks[model_id] = result

    failures = [
        model_id
        for model_id, result in checks.items()
        if result.get("manifest_rows_match") is False
        or result.get("exact_duplicate_rows", 0) > 0
        or result.get("secret_pattern_matches", 0) > 0
        or result.get("model_field_valid") is False
        or result.get("all_final_steps") is False
        or result.get("observed_model_valid") is False
    ]
    report = {
        "bytes": total_bytes,
        "megabytes": round(total_bytes / 1024 / 1024, 2),
        "checks": checks,
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
