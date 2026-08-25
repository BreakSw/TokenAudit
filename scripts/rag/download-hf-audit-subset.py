from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

import pyarrow as pa
import pyarrow.parquet as pq
import requests
from huggingface_hub import HfApi


HF_BASE = "https://huggingface.co/datasets"
DATASET_SERVER = "https://datasets-server.huggingface.co"
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"Bearer\s+[A-Za-z0-9._~-]{24,}", re.IGNORECASE),
)


def stable_score(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest(), 16)


def json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        for pattern in SECRET_PATTERNS:
            value = pattern.sub("<TOKENAUDIT_REDACTED_SECRET>", value)
        return value
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items()}
    return value


class Downloader:
    def __init__(self, output_root: Path, temp_root: Path) -> None:
        self.output_root = output_root
        self.temp_root = temp_root
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TokenAudit-RAG-Dataset-Selector/1.0"})
        self.hf = HfApi()
        self.results: list[dict[str, Any]] = []

    def request(self, url: str, *, stream: bool = False) -> requests.Response:
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                response = self.session.get(url, stream=stream, timeout=(30, 180))
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt == 3:
                    break
                time.sleep(2**attempt)
        raise RuntimeError(f"Failed to download {url}: {last_error}")

    @staticmethod
    def resolve_url(repo: str, path: str) -> str:
        return f"{HF_BASE}/{repo}/resolve/main/{quote(path, safe='/')}"

    def iter_jsonl(self, repo: str, path: str) -> Iterable[dict[str, Any]]:
        response = self.request(self.resolve_url(repo, path), stream=True)
        try:
            for raw_line in response.iter_lines():
                if raw_line:
                    yield json.loads(raw_line)
        finally:
            response.close()

    def download_file(self, repo: str, path: str, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".part")
        response = self.request(self.resolve_url(repo, path), stream=True)
        try:
            with temporary.open("wb") as output:
                for block in response.iter_content(chunk_size=1024 * 1024):
                    if block:
                        output.write(block)
        finally:
            response.close()
        temporary.replace(target)

    @staticmethod
    def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> tuple[int, int]:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".part")
        count = 0
        with temporary.open("wb") as output:
            for row in rows:
                output.write(json_bytes(sanitize(row)))
                count += 1
        temporary.replace(path)
        return count, path.stat().st_size

    def record(
        self,
        *,
        model_id: str,
        repo: str | None,
        output: Path | None,
        rows: int,
        selection: str,
        confidence: str,
    ) -> None:
        self.results.append(
            {
                "model_id": model_id,
                "repository": repo,
                "source_url": f"{HF_BASE}/{repo}" if repo else None,
                "output": (
                    output.relative_to(self.output_root).as_posix() if output else None
                ),
                "rows": rows,
                "bytes": output.stat().st_size if output else 0,
                "selection": selection,
                "confidence": confidence,
            }
        )

    def download_fable(self) -> None:
        repo = "Glint-Research/Fable-5-traces"
        candidates: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
        last_by_session: dict[str, dict[str, Any]] = {}
        for row in self.iter_jsonl(repo, "fable5_cot_merged.jsonl"):
            if row.get("model") != "claude-fable-5":
                continue
            session_id = str(row.get("session") or row.get("source_file") or "unknown")
            uid = str(row.get("uid") or hashlib.sha256(json_bytes(row)).hexdigest())
            bucket = candidates[session_id]
            bucket.append((stable_score(uid), row))
            bucket.sort(key=lambda item: item[0])
            del bucket[9:]
            last_by_session[session_id] = row

        guaranteed = list(last_by_session.values())
        seen = {str(row.get("uid")) for row in guaranteed}
        remaining = sorted(
            (
                (score, row)
                for bucket in candidates.values()
                for score, row in bucket
                if str(row.get("uid")) not in seen
            ),
            key=lambda item: item[0],
        )
        selected = guaranteed + [row for _, row in remaining[: 500 - len(guaranteed)]]
        selected.sort(key=lambda row: (str(row.get("session")), str(row.get("uid"))))
        target = self.output_root / "claude-fable-5" / "selected.jsonl"
        count, _ = self.write_jsonl(target, selected)
        self.record(
            model_id="claude-fable-5",
            repo=repo,
            output=target,
            rows=count,
            selection="500 deterministic rows covering every available source session",
            confidence="high for captured coding-agent behavior",
        )

    def download_opus(self) -> None:
        repo = "TeichAI/Claude-Opus-4.6-Reasoning-887x"
        target = self.output_root / "claude-opus-4.6" / "selected.parquet"
        self.download_file(repo, "data/train-00000-of-00001.parquet", target)
        table = pq.read_table(target)
        sanitized_rows = [sanitize(row) for row in table.to_pylist()]
        pq.write_table(pa.Table.from_pylist(sanitized_rows), target, compression="zstd")
        rows = len(sanitized_rows)
        self.record(
            model_id="claude-opus-4.6",
            repo=repo,
            output=target,
            rows=rows,
            selection="complete Parquet split",
            confidence="medium; source-asserted high-reasoning distillation",
        )

    def dataset_rows(self, repo: str, offset: int, length: int) -> list[dict[str, Any]]:
        url = (
            f"{DATASET_SERVER}/rows?dataset={quote(repo, safe='')}"
            f"&config=default&split=train&offset={offset}&length={length}"
        )
        payload = self.request(url).json()
        return [item["row"] for item in payload.get("rows", [])]

    def download_deepseek(self) -> None:
        repo = "TeichAI/DeepSeek-v4-Pro-Agent"
        total_rows = 4006
        block_size = 50
        offsets = [round(index * (total_rows - block_size) / 7) for index in range(8)]
        selected: dict[str, dict[str, Any]] = {}
        for offset in offsets:
            for row in self.dataset_rows(repo, offset, block_size):
                session_id = str(row.get("session_id") or row.get("file_path"))
                selected[session_id] = row
        target = self.output_root / "deepseek-v4-pro" / "selected.jsonl"
        count, _ = self.write_jsonl(
            target, (selected[key] for key in sorted(selected, key=stable_score))
        )
        self.record(
            model_id="deepseek-v4-pro",
            repo=repo,
            output=target,
            rows=count,
            selection="8 evenly spaced blocks, deduplicated by session_id",
            confidence="high for captured agent/tool behavior",
        )

    def download_glm(self) -> None:
        repo = "AletheiaResearch/GLM-5.2-Bench"
        info = self.hf.dataset_info(repo, files_metadata=True)
        files = sorted(
            sibling.rfilename
            for sibling in info.siblings
            if sibling.rfilename.endswith(".jsonl")
            and sibling.rfilename.startswith(("passed/", "failed/"))
        )
        rows: list[dict[str, Any]] = []
        for filename in files:
            outcome = filename.split("/", 1)[0]
            for row in self.iter_jsonl(repo, filename):
                row["tokenaudit_benchmark_outcome"] = outcome
                row["tokenaudit_source_file"] = filename
                rows.append(row)
        target = self.output_root / "glm-5.2" / "selected.jsonl"
        count, _ = self.write_jsonl(target, rows)
        self.record(
            model_id="glm-5.2",
            repo=repo,
            output=target,
            rows=count,
            selection="all passed and failed benchmark sessions",
            confidence="high for benchmark-observed agent behavior",
        )

    def download_luna(self) -> None:
        repo = "empero-ai/gpt-5.6-luna-sft-900x"
        target = self.output_root / "gpt-5.6-luna" / "selected.jsonl"
        rows, _ = self.write_jsonl(target, self.iter_jsonl(repo, "sft.jsonl"))
        self.record(
            model_id="gpt-5.6-luna",
            repo=repo,
            output=target,
            rows=rows,
            selection="complete compact SFT set",
            confidence="medium; persona-injected distillation must not define native style",
        )

    @staticmethod
    def keep_smallest(
        bucket: list[tuple[int, dict[str, Any]]],
        score: int,
        row: dict[str, Any],
        limit: int,
    ) -> None:
        bucket.append((score, row))
        bucket.sort(key=lambda item: item[0])
        del bucket[limit:]

    def download_sol(self) -> None:
        repo = "greghavens/gpt-5.6-sol-coding-and-debugging-traces"
        by_category: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
        for row in self.iter_jsonl(repo, "traces.jsonl"):
            if row.get("teacher_model") != "gpt-5.6-sol":
                continue
            if row.get("assistant_step") != row.get("assistant_steps"):
                continue
            trajectory_id = str(row.get("source_trajectory_id"))
            category = str(row.get("category") or row.get("domain") or "other")
            self.keep_smallest(
                by_category[category], stable_score(trajectory_id), row, limit=30
            )

        chosen: list[dict[str, Any]] = []
        chosen_ids: set[str] = set()
        for category in sorted(by_category):
            for _, row in by_category[category][:3]:
                trajectory_id = str(row.get("source_trajectory_id"))
                if trajectory_id not in chosen_ids:
                    chosen.append(row)
                    chosen_ids.add(trajectory_id)
        remainder = sorted(
            (
                (score, row)
                for bucket in by_category.values()
                for score, row in bucket
                if str(row.get("source_trajectory_id")) not in chosen_ids
            ),
            key=lambda item: item[0],
        )
        for _, row in remainder:
            trajectory_id = str(row.get("source_trajectory_id"))
            if trajectory_id in chosen_ids:
                continue
            chosen.append(row)
            chosen_ids.add(trajectory_id)
            if len(chosen) >= 300:
                break

        target = self.output_root / "gpt-5.6-sol" / "selected.jsonl"
        count, _ = self.write_jsonl(
            target,
            sorted(chosen, key=lambda row: str(row.get("source_trajectory_id"))),
        )
        self.record(
            model_id="gpt-5.6-sol",
            repo=repo,
            output=target,
            rows=count,
            selection="one final full-context row per trajectory, category-stratified",
            confidence="high for verified coding, review, and tool behavior",
        )

    def download_kimi(self) -> None:
        repo = "greghavens/kimi-k3-coding-and-debugging-traces"
        info = self.hf.dataset_info(repo, files_metadata=True)
        files = sorted(
            sibling.rfilename
            for sibling in info.siblings
            if sibling.rfilename.startswith("data/")
            and sibling.rfilename.endswith(".parquet")
        )
        with tempfile.TemporaryDirectory(dir=self.temp_root) as temporary_directory:
            tables = []
            temporary_root = Path(temporary_directory)
            for index, filename in enumerate(files):
                local_file = temporary_root / f"{index:04d}.parquet"
                self.download_file(repo, filename, local_file)
                tables.append(pq.read_table(local_file))
            table = pa.concat_tables(tables, promote_options="default")
            rows = table.to_pylist()

        by_trajectory: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            trajectory_id = str(row.get("source_trajectory_id"))
            by_trajectory[trajectory_id].append(row)
        selected: list[dict[str, Any]] = []
        for trajectory_rows in by_trajectory.values():
            ordered = sorted(
                trajectory_rows, key=lambda row: int(row.get("assistant_step") or 0)
            )
            selected.append(ordered[-1])
            if len(ordered) >= 4:
                selected.append(ordered[len(ordered) // 2])

        target = self.output_root / "kimi-k3" / "selected.parquet"
        target.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(
            pa.Table.from_pylist([sanitize(row) for row in selected]),
            target,
            compression="zstd",
        )
        self.record(
            model_id="kimi-k3",
            repo=repo,
            output=target,
            rows=len(selected),
            selection="final row plus one midpoint for trajectories with at least four steps",
            confidence=(
                "medium-high; observed_models identifies moonshotai/kimi-k3, "
                "but rows are not model-attested"
            ),
        )

    def record_terra_gap(self) -> None:
        self.record(
            model_id="gpt-5.6-terra",
            repo=None,
            output=None,
            rows=0,
            selection="not downloaded: no verified public Terra rows found",
            confidence="unavailable",
        )

    def finish(self) -> None:
        generated_files = [path for path in self.output_root.rglob("*") if path.is_file()]
        data_bytes = sum(path.stat().st_size for path in generated_files)
        manifest = {
            "schema_version": 1,
            "selection_name": "huggingface-selected-v1",
            "selection_policy": (
                "Quality-first approximate 500 MB target; no hard byte cutoff. "
                "Large repositories are streamed and only selected rows are persisted."
            ),
            "data_bytes_before_manifest": data_bytes,
            "models": self.results,
        }
        manifest_path = self.output_root / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        total_bytes = sum(
            path.stat().st_size for path in self.output_root.rglob("*") if path.is_file()
        )
        print(
            json.dumps(
                {
                    "models": len(self.results),
                    "models_with_rows": sum(item["rows"] > 0 for item in self.results),
                    "rows": sum(item["rows"] for item in self.results),
                    "bytes": total_bytes,
                    "megabytes": round(total_bytes / 1024 / 1024, 2),
                    "manifest": str(manifest_path),
                },
                ensure_ascii=False,
            )
        )

    def run(self) -> None:
        self.output_root.mkdir(parents=True, exist_ok=True)
        for label, handler in (
            ("claude-fable-5", self.download_fable),
            ("claude-opus-4.6", self.download_opus),
            ("deepseek-v4-pro", self.download_deepseek),
            ("glm-5.2", self.download_glm),
            ("gpt-5.6-luna", self.download_luna),
            ("gpt-5.6-sol", self.download_sol),
            ("kimi-k3", self.download_kimi),
        ):
            print(f"Selecting {label} ...", flush=True)
            handler()
        self.record_terra_gap()
        self.finish()


def main() -> int:
    parser = argparse.ArgumentParser(description="Download the compact TokenAudit HF set")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--temp-dir", type=Path, required=True)
    args = parser.parse_args()
    args.temp_dir.mkdir(parents=True, exist_ok=True)
    Downloader(args.output.resolve(), args.temp_dir.resolve()).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
