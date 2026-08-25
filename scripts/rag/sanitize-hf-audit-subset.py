from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq


SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"Bearer\s+[A-Za-z0-9._~-]{24,}", re.IGNORECASE),
)


def sanitize(value: Any) -> tuple[Any, int]:
    if isinstance(value, str):
        replacements = 0
        for pattern in SECRET_PATTERNS:
            value, count = pattern.subn("<TOKENAUDIT_REDACTED_SECRET>", value)
            replacements += count
        return value, replacements
    if isinstance(value, list):
        result = []
        replacements = 0
        for item in value:
            cleaned, count = sanitize(item)
            result.append(cleaned)
            replacements += count
        return result, replacements
    if isinstance(value, dict):
        result = {}
        replacements = 0
        for key, item in value.items():
            cleaned, count = sanitize(item)
            result[key] = cleaned
            replacements += count
        return result, replacements
    return value, 0


def sanitize_jsonl(path: Path) -> int:
    temporary = path.with_suffix(path.suffix + ".part")
    replacements = 0
    with path.open(encoding="utf-8") as source, temporary.open(
        "w", encoding="utf-8", newline="\n"
    ) as output:
        for line in source:
            if not line.strip():
                continue
            cleaned, count = sanitize(json.loads(line))
            replacements += count
            output.write(
                json.dumps(cleaned, ensure_ascii=False, separators=(",", ":")) + "\n"
            )
    temporary.replace(path)
    return replacements


def sanitize_parquet(path: Path) -> int:
    rows = pq.read_table(path).to_pylist()
    cleaned_rows = []
    replacements = 0
    for row in rows:
        cleaned, count = sanitize(row)
        cleaned_rows.append(cleaned)
        replacements += count
    if replacements:
        temporary = path.with_suffix(path.suffix + ".part")
        pq.write_table(pa.Table.from_pylist(cleaned_rows), temporary, compression="zstd")
        temporary.replace(path)
    return replacements


def main() -> int:
    parser = argparse.ArgumentParser(description="Redact secret-like values in HF data")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    total_replacements = 0
    per_model: dict[str, int] = {}

    for model in manifest["models"]:
        if not model["output"]:
            continue
        path = root / model["output"]
        replacements = (
            sanitize_jsonl(path) if path.suffix == ".jsonl" else sanitize_parquet(path)
        )
        total_replacements += replacements
        per_model[model["model_id"]] = replacements
        model["bytes"] = path.stat().st_size

    manifest["data_bytes_before_manifest"] = sum(
        path.stat().st_size
        for path in root.rglob("*")
        if path.is_file() and path != manifest_path
    )
    manifest["secret_redaction"] = {
        "placeholder": "<TOKENAUDIT_REDACTED_SECRET>",
        "replacements": total_replacements,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"replacements": total_replacements, "models": per_model}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
