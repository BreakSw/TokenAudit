from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator

from llama_index.core.ingestion import DocstoreStrategy, IngestionPipeline
from llama_index.core.schema import TextNode
from llama_index.core.storage.docstore import SimpleDocumentStore

from .behavior_schema import BehaviorRecord


_SPACE_RE = re.compile(r"\s+")
_CODE_RE = re.compile(r"```|\b(?:def|class|function|const|let|SELECT|public static)\b", re.I)
_SELF_CORRECTION_RE = re.compile(
    r"\b(?:actually|correction|instead|recheck|re-check|my mistake|let me revise)\b|"
    r"(?:更正|重新检查|我刚才|应当改为|修正)",
    re.I,
)
_VERIFY_RE = re.compile(
    r"\b(?:tests?|pytest|verify|verification|lint|build|compile|assert)\b|"
    r"(?:测试|验证|编译|断言|检查结果)",
    re.I,
)
_REFUSAL_RE = re.compile(
    r"\b(?:cannot|can't|unable|won't|not able to)\b|(?:无法|不能|拒绝)",
    re.I,
)


def load_behavior_records(dataset_root: Path) -> tuple[list[BehaviorRecord], dict[str, Any]]:
    manifest_path = dataset_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records: list[BehaviorRecord] = []
    per_model_input: dict[str, int] = {}

    for model in manifest.get("models", []):
        output = model.get("output")
        if not output:
            continue
        model_id = str(model["model_id"])
        source_path = dataset_root / str(output)
        rows = list(_iter_rows(source_path))
        per_model_input[model_id] = len(rows)
        if model_id == "glm-5.2":
            rows = _group_glm_events(rows)
        for index, row in enumerate(rows):
            record = _normalize_row(
                model_id=model_id,
                source_id=str(model.get("repository") or source_path.name),
                confidence_text=str(model.get("confidence") or "medium"),
                row=row,
                row_index=index,
            )
            if record is not None:
                records.append(record)

    unique_records, duplicates_removed = _deduplicate_with_llamaindex(records)
    stats = {
        "schema_version": 1,
        "input_rows": sum(per_model_input.values()),
        "input_rows_by_model": per_model_input,
        "normalized_records": len(records),
        "unique_records": len(unique_records),
        "duplicates_removed": duplicates_removed,
        "records_by_model": _count_by_model(unique_records),
        "dedup_engine": "llama-index-core",
        "dedup_strategy": "DocstoreStrategy.DUPLICATES_ONLY",
    }
    return unique_records, stats


def write_behavior_records(
    records: Iterable[BehaviorRecord],
    output_path: Path,
    stats: dict[str, Any],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    stats_path = output_path.with_name("stats.json")
    stats_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_behavior_profile_cards(
    records: list[BehaviorRecord],
    *,
    max_task_groups_per_model: int = 4,
) -> list[BehaviorRecord]:
    """Aggregate clean trace observations into compact, retrievable profiles.

    A model contributes one all-task card plus at most four cards for its most
    represented task groups.  Persona-contaminated traces are excluded before
    aggregation so they cannot influence either the overall card or a task
    card.  A model with no clean observations is intentionally omitted.
    """

    by_model: dict[str, list[BehaviorRecord]] = defaultdict(list)
    for record in records:
        by_model[record.model_id].append(record)

    cards: list[BehaviorRecord] = []
    for model_id, model_records in sorted(by_model.items()):
        clean_records = [
            record for record in model_records if not record.persona_contaminated
        ]
        if not clean_records:
            continue
        task_groups: dict[str, list[BehaviorRecord]] = defaultdict(list)
        for record in clean_records:
            task_groups[record.task_type].append(record)
        selected_groups = sorted(
            task_groups.items(), key=lambda item: (-len(item[1]), item[0])
        )[:max_task_groups_per_model]
        cards.append(_profile_card(model_id, "all_tasks", clean_records))
        cards.extend(
            _profile_card(model_id, task_type, group)
            for task_type, group in selected_groups
        )
    return cards


def select_behavior_evidence_records(
    records: list[BehaviorRecord],
    *,
    samples_per_model: int = 20,
) -> list[BehaviorRecord]:
    """Select a small, balanced first embedding tranche from clean traces.

    Selection is deterministic and round-robins across task types.  Within a
    task type it prefers attested, high-confidence observations with known
    outcomes and useful observable behavior, instead of taking the first rows
    from each source file.
    """

    if samples_per_model < 0:
        raise ValueError("samples_per_model must be non-negative")
    by_model: dict[str, list[BehaviorRecord]] = defaultdict(list)
    for record in records:
        if not record.persona_contaminated:
            by_model[record.model_id].append(record)

    selected: list[BehaviorRecord] = []
    for model_id in sorted(by_model):
        by_task: dict[str, list[BehaviorRecord]] = defaultdict(list)
        for record in by_model[model_id]:
            by_task[record.task_type].append(record)
        queues = {
            task_type: sorted(group, key=_evidence_priority)
            for task_type, group in by_task.items()
        }
        task_order = sorted(queues, key=lambda task: (-len(queues[task]), task))
        model_selection: list[BehaviorRecord] = []
        while len(model_selection) < samples_per_model:
            added = False
            for task_type in task_order:
                queue = queues[task_type]
                if queue and len(model_selection) < samples_per_model:
                    model_selection.append(queue.pop(0))
                    added = True
            if not added:
                break
        selected.extend(model_selection)
    return selected


def _evidence_priority(record: BehaviorRecord) -> tuple[Any, ...]:
    informative_tags = len(set(record.behavior_tags) - {"plain_response"})
    response_length = len(record.response_excerpt)
    useful_length = 1 if 200 <= response_length <= 2600 else 0
    return (
        record.observed_only,
        -(record.outcome in {"success", "failure"}),
        -record.confidence,
        -informative_tags,
        -useful_length,
        -min(response_length, 2600),
        record.id,
    )


def write_profile_cards(cards: list[BehaviorRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for card in cards:
            handle.write(json.dumps(card.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")


def _iter_rows(path: Path) -> Iterator[dict[str, Any]]:
    if path.suffix.casefold() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    if isinstance(row, dict):
                        yield row
        return

    if path.suffix.casefold() == ".parquet":
        import pandas as pd

        for row in pd.read_parquet(path).to_dict("records"):
            yield _to_builtin(row)
        return
    raise ValueError(f"Unsupported behavior dataset: {path}")


def _group_glm_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("tokenaudit_source_file") or "unknown")].append(row)
    trajectories: list[dict[str, Any]] = []
    for source_file, events in grouped.items():
        messages = [
            event["message"]
            for event in events
            if event.get("type") == "message" and isinstance(event.get("message"), dict)
        ]
        model_change = next(
            (event for event in events if event.get("type") == "model_change"),
            {},
        )
        trajectories.append(
            {
                "messages": messages,
                "tokenaudit_benchmark_outcome": next(
                    (event.get("tokenaudit_benchmark_outcome") for event in events if event.get("tokenaudit_benchmark_outcome")),
                    "unknown",
                ),
                "tokenaudit_source_file": source_file,
                "modelId": model_change.get("modelId"),
                "provider": model_change.get("provider"),
                "sample_kind": "benchmark_trajectory",
            }
        )
    return trajectories


def _normalize_row(
    *,
    model_id: str,
    source_id: str,
    confidence_text: str,
    row: dict[str, Any],
    row_index: int,
) -> BehaviorRecord | None:
    messages = _messages(row.get("messages"))
    task = _first_non_empty(
        _first_role_text(messages, "user"),
        row.get("prompt"),
        row.get("context"),
        row.get("task"),
        row.get("topic"),
    )
    response = _first_non_empty(
        _last_role_text(messages, "assistant"),
        _observable_output(row.get("output")),
        row.get("completion"),
    )
    if not task and not response:
        return None

    trajectory_id = str(
        _first_non_empty(
            row.get("session_id"),
            row.get("session"),
            row.get("source_trajectory_id"),
            row.get("uid"),
            row.get("id"),
            row.get("tokenaudit_source_file"),
            f"row-{row_index}",
        )
    )
    task_type = _task_type(row, task)
    outcome = _outcome(row)
    tool_calls = _tool_call_count(row, messages)
    assistant_turns = sum(1 for message in messages if _role(message) == "assistant")
    user_turns = sum(1 for message in messages if _role(message) == "user")
    tags = _behavior_tags(response, tool_calls)
    task_excerpt = _clean(task)[:1800]
    response_excerpt = _clean(response)[:3200]
    confidence = _confidence(confidence_text)
    persona_contaminated = model_id == "gpt-5.6-luna"
    observed_only = model_id == "kimi-k3" or not bool(row.get("model_attested", True))
    sample_kind = str(row.get("sample_kind") or ("agent_trajectory" if tool_calls else "response"))
    embedding_text = _embedding_text(
        task_type=task_type,
        outcome=outcome,
        assistant_turns=assistant_turns,
        user_turns=user_turns,
        tool_calls=tool_calls,
        tags=tags,
        task=task_excerpt,
        response=response_excerpt,
    )
    content_hash = hashlib.sha256(embedding_text.encode("utf-8")).hexdigest()
    record_id = hashlib.sha256(
        f"{model_id}|{trajectory_id}|{row_index}|{content_hash}".encode("utf-8")
    ).hexdigest()[:32]
    return BehaviorRecord(
        id=f"behavior-{record_id}",
        model_id=model_id,
        source_id=source_id,
        trajectory_id=trajectory_id[:128],
        sample_kind=sample_kind[:32],
        task_type=task_type[:64],
        outcome=outcome[:24],
        confidence=confidence,
        persona_contaminated=persona_contaminated,
        observed_only=observed_only,
        tool_call_count=tool_calls,
        assistant_turns=assistant_turns,
        user_turns=user_turns,
        behavior_tags=tuple(tags),
        task_excerpt=task_excerpt,
        response_excerpt=response_excerpt,
        embedding_text=embedding_text[:8192],
        content_hash=content_hash,
    )


def _messages(value: Any) -> list[dict[str, Any]]:
    value = _to_builtin(value)
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return []
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _to_builtin(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _to_builtin(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_builtin(item) for item in value]
    if hasattr(value, "tolist"):
        return _to_builtin(value.tolist())
    return value


def _role(message: dict[str, Any]) -> str:
    return str(message.get("role") or "").casefold()


def _message_content(message: dict[str, Any]) -> str:
    return _clean(_text(message.get("content")))


def _first_role_text(messages: list[dict[str, Any]], role: str) -> str:
    return next((_message_content(item) for item in messages if _role(item) == role and _message_content(item)), "")


def _last_role_text(messages: list[dict[str, Any]], role: str) -> str:
    return next((_message_content(item) for item in reversed(messages) if _role(item) == role and _message_content(item)), "")


def _observable_output(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("content", "text", "output", "answer", "message"):
            if key in value:
                return _text(value[key])
    return _text(value)


def _text(value: Any) -> str:
    value = _to_builtin(value)
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "content", "value"):
            if key in value:
                return _text(value[key])
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, list):
        return "\n".join(part for part in (_text(item) for item in value) if part)
    return str(value)


def _clean(value: Any) -> str:
    return _SPACE_RE.sub(" ", _text(value)).strip()


def _first_non_empty(*values: Any) -> str:
    for value in values:
        text = _clean(value)
        if text:
            return text
    return ""


def _task_type(row: dict[str, Any], task: str) -> str:
    explicit = _first_non_empty(row.get("category"), row.get("topic"), row.get("domain"), row.get("harness"))
    if explicit:
        canonical = _canonical_task_type(explicit)
        if canonical != "general_reasoning":
            return canonical
    lowered = task.casefold()
    if _CODE_RE.search(task):
        return "coding"
    if any(word in lowered for word in ("proof", "equation", "calculate", "math", "定理", "计算")):
        return "reasoning_math"
    if any(word in lowered for word in ("tool", "browser", "terminal", "file", "工具", "文件")):
        return "tool_use"
    return "general_reasoning"


def _canonical_task_type(value: str) -> str:
    lowered = value.casefold()
    mappings = (
        ("agentic_coding", ("agent", "swe", "codex", "repo")),
        ("coding_debug", ("code", "coding", "debug", "program", "software")),
        ("reasoning_math", ("math", "proof", "logic", "reasoning", "calculate")),
        ("tool_use", ("tool", "browser", "terminal", "computer")),
        ("security", ("security", "vulnerability", "exploit", "cyber")),
        ("data_analysis", ("data", "sql", "analysis", "spreadsheet")),
        ("writing", ("write", "writing", "essay", "creative", "summary")),
    )
    for task_type, needles in mappings:
        if any(needle in lowered for needle in needles):
            return task_type
    return "general_reasoning"


def _outcome(row: dict[str, Any]) -> str:
    explicit = _first_non_empty(row.get("tokenaudit_benchmark_outcome"), row.get("outcome"), row.get("status"))
    if explicit:
        lowered = explicit.casefold()
        if any(item in lowered for item in ("pass", "success", "correct")):
            return "success"
        if any(item in lowered for item in ("fail", "error", "incorrect")):
            return "failure"
        return lowered[:24]
    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        for key in ("success", "passed", "outcome", "status"):
            if key in metadata:
                value = metadata[key]
                if value is True:
                    return "success"
                if value is False:
                    return "failure"
                return _clean(value).casefold()[:24] or "unknown"
    return "unknown"


def _tool_call_count(row: dict[str, Any], messages: list[dict[str, Any]]) -> int:
    explicit = row.get("num_tool_calls")
    if isinstance(explicit, int):
        return max(0, explicit)
    count = 0
    for message in messages:
        calls = _to_builtin(message.get("tool_calls"))
        if isinstance(calls, list):
            count += len(calls)
        if _role(message) in {"tool", "function"}:
            count += 1
    tools_used = _to_builtin(row.get("tools_used"))
    if not count and isinstance(tools_used, list):
        count = len(tools_used)
    return count


def _behavior_tags(response: str, tool_calls: int) -> list[str]:
    tags: list[str] = []
    if tool_calls:
        tags.append("uses_tools")
    if _CODE_RE.search(response):
        tags.append("code_output")
    if _SELF_CORRECTION_RE.search(response):
        tags.append("self_correction")
    if _VERIFY_RE.search(response):
        tags.append("verification_oriented")
    if _REFUSAL_RE.search(response):
        tags.append("refusal_or_uncertainty")
    stripped = response.strip()
    if stripped.startswith(("{", "[")):
        tags.append("structured_output")
    if len(response) > 2000:
        tags.append("long_form")
    elif 0 < len(response) < 400:
        tags.append("concise")
    return tags or ["plain_response"]


def _confidence(value: str) -> float:
    lowered = value.casefold()
    if "medium-high" in lowered:
        return 0.8
    if "high" in lowered:
        return 0.9
    if "medium" in lowered:
        return 0.65
    if "low" in lowered:
        return 0.4
    return 0.5


def _embedding_text(
    *,
    task_type: str,
    outcome: str,
    assistant_turns: int,
    user_turns: int,
    tool_calls: int,
    tags: list[str],
    task: str,
    response: str,
) -> str:
    return "\n".join(
        (
            f"Task type: {task_type}",
            f"Observed outcome: {outcome}",
            f"Conversation shape: user_turns={user_turns}, assistant_turns={assistant_turns}, tool_calls={tool_calls}",
            f"Observable behavior tags: {', '.join(tags)}",
            f"Task excerpt: {task}",
            f"Final observable response excerpt: {response}",
        )
    )


def _deduplicate_with_llamaindex(records: list[BehaviorRecord]) -> tuple[list[BehaviorRecord], int]:
    nodes = [
        TextNode(id_=record.id, text=f"{record.model_id}\n{record.embedding_text}")
        for record in records
    ]
    pipeline = IngestionPipeline(
        transformations=[],
        docstore=SimpleDocumentStore(),
        docstore_strategy=DocstoreStrategy.DUPLICATES_ONLY,
    )
    unique_nodes = pipeline.run(nodes=nodes)
    by_id = {record.id: record for record in records}
    unique = [by_id[node.node_id] for node in unique_nodes]
    return unique, len(records) - len(unique)


def _count_by_model(records: Iterable[BehaviorRecord]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for record in records:
        counts[record.model_id] += 1
    return dict(sorted(counts.items()))


def _profile_card(model_id: str, task_type: str, records: list[BehaviorRecord]) -> BehaviorRecord:
    outcomes = Counter(record.outcome for record in records)
    tags = Counter(tag for record in records for tag in record.behavior_tags)
    sample_count = len(records)
    avg_tool_calls = sum(record.tool_call_count for record in records) / sample_count
    avg_assistant_turns = sum(record.assistant_turns for record in records) / sample_count
    avg_response_chars = sum(len(record.response_excerpt) for record in records) / sample_count
    top_tags = [tag for tag, _ in tags.most_common(8)]
    representatives = sorted(
        records,
        key=lambda record: (-record.confidence, -len(record.response_excerpt), record.id),
    )[:3]
    task_examples = " | ".join(record.task_excerpt[:350] for record in representatives if record.task_excerpt)
    response_examples = " | ".join(record.response_excerpt[:550] for record in representatives if record.response_excerpt)
    outcome_text = ", ".join(f"{key}={value}" for key, value in sorted(outcomes.items()))
    tag_text = ", ".join(
        f"{key}={value / sample_count:.1%}" for key, value in tags.most_common(10)
    )
    embedding_text = "\n".join(
        (
            f"Behavior profile scope: {task_type}",
            f"Observed samples: {sample_count}; outcomes: {outcome_text}",
            f"Average observable shape: assistant_turns={avg_assistant_turns:.2f}, tool_calls={avg_tool_calls:.2f}, response_chars={avg_response_chars:.0f}",
            f"Observable tag rates: {tag_text}",
            f"Representative task excerpts: {task_examples}",
            f"Representative final-response excerpts: {response_examples}",
        )
    )[:8192]
    content_hash = hashlib.sha256(embedding_text.encode("utf-8")).hexdigest()
    card_id = hashlib.sha256(f"{model_id}|{task_type}|{content_hash}".encode("utf-8")).hexdigest()[:32]
    return BehaviorRecord(
        id=f"profile-{card_id}",
        model_id=model_id,
        source_id="aggregated:huggingface-selected-v1",
        trajectory_id=f"profile:{task_type}",
        sample_kind="behavior_profile",
        task_type=task_type,
        outcome="mixed" if len(outcomes) > 1 else next(iter(outcomes), "unknown"),
        confidence=round(sum(record.confidence for record in records) / sample_count, 4),
        persona_contaminated=any(record.persona_contaminated for record in records),
        observed_only=all(record.observed_only for record in records),
        tool_call_count=round(avg_tool_calls),
        assistant_turns=round(avg_assistant_turns),
        user_turns=round(sum(record.user_turns for record in records) / sample_count),
        behavior_tags=tuple(top_tags),
        task_excerpt=task_examples[:1800],
        response_excerpt=response_examples[:3200],
        embedding_text=embedding_text,
        content_hash=content_hash,
    )
