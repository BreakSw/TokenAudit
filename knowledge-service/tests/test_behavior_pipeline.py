from __future__ import annotations

import json

from tokenaudit_knowledge.behavior_pipeline import (
    build_behavior_profile_cards,
    load_behavior_records,
    select_behavior_evidence_records,
)
from tokenaudit_knowledge.behavior_schema import BehaviorRecord


def test_normalizes_messages_and_marks_persona(tmp_path):
    root = tmp_path
    model_dir = root / "gpt-5.6-luna"
    model_dir.mkdir()
    (model_dir / "selected.jsonl").write_text(
        json.dumps(
            {
                "id": "one",
                "topic": "coding",
                "messages": [
                    {"role": "user", "content": "Fix the failing function"},
                    {"role": "assistant", "content": "I will update it and run tests."},
                ],
            }
        ) + "\n",
        encoding="utf-8",
    )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_id": "gpt-5.6-luna",
                        "repository": "example/luna",
                        "output": "gpt-5.6-luna/selected.jsonl",
                        "confidence": "medium; persona-injected",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    records, stats = load_behavior_records(root)

    assert stats["unique_records"] == 1
    assert records[0].persona_contaminated is True
    assert "verification_oriented" in records[0].behavior_tags
    assert "Fix the failing function" in records[0].embedding_text


def test_glm_events_become_one_trajectory(tmp_path):
    model_dir = tmp_path / "glm-5.2"
    model_dir.mkdir()
    rows = [
        {"type": "session", "id": "s1", "tokenaudit_source_file": "case.jsonl", "tokenaudit_benchmark_outcome": "passed"},
        {"type": "message", "message": {"role": "user", "content": "Solve this"}, "tokenaudit_source_file": "case.jsonl", "tokenaudit_benchmark_outcome": "passed"},
        {"type": "message", "message": {"role": "assistant", "content": "Solved"}, "tokenaudit_source_file": "case.jsonl", "tokenaudit_benchmark_outcome": "passed"},
    ]
    (model_dir / "selected.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_id": "glm-5.2",
                        "repository": "example/glm",
                        "output": "glm-5.2/selected.jsonl",
                        "confidence": "high",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    records, stats = load_behavior_records(tmp_path)

    assert stats["input_rows"] == 3
    assert stats["unique_records"] == 1
    assert records[0].outcome == "success"
    assert records[0].sample_kind == "benchmark_trajectory"


def test_builds_dense_profile_cards_from_observations(tmp_path):
    model_dir = tmp_path / "deepseek-v4-pro"
    model_dir.mkdir()
    rows = [
        {"session_id": "a", "prompt": "Debug this code", "messages": [{"role": "assistant", "content": "I will patch and test it."}], "num_tool_calls": 2},
        {"session_id": "b", "prompt": "Debug another function", "messages": [{"role": "assistant", "content": "Run tests after the fix."}], "num_tool_calls": 1},
    ]
    (model_dir / "selected.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"models": [{"model_id": "deepseek-v4-pro", "repository": "example/deepseek", "output": "deepseek-v4-pro/selected.jsonl", "confidence": "high"}]}),
        encoding="utf-8",
    )
    records, _ = load_behavior_records(tmp_path)
    cards = build_behavior_profile_cards(records)
    assert any(card.task_type == "all_tasks" for card in cards)
    assert all(card.sample_kind == "behavior_profile" for card in cards)
    assert "Observed samples: 2" in cards[0].embedding_text


def test_profile_cards_exclude_persona_contaminated_models(tmp_path):
    model_dir = tmp_path / "gpt-5.6-luna"
    model_dir.mkdir()
    (model_dir / "selected.jsonl").write_text(
        json.dumps(
            {
                "id": "persona-one",
                "prompt": "Answer in the injected persona",
                "completion": "A persona-shaped answer",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_id": "gpt-5.6-luna",
                        "repository": "example/luna-persona",
                        "output": "gpt-5.6-luna/selected.jsonl",
                        "confidence": "medium; persona-injected",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    records, _ = load_behavior_records(tmp_path)
    cards = build_behavior_profile_cards(records)

    assert cards == []


def test_profile_cards_keep_only_four_largest_task_groups(tmp_path):
    model_dir = tmp_path / "deepseek-v4-pro"
    model_dir.mkdir()
    task_types = ["coding", "math", "tool", "security", "writing", "general"]
    rows = [
        {
            "id": f"sample-{index}",
            "category": task_type,
            "prompt": f"Task {index}",
            "completion": f"Observable response {index}",
        }
        for index, task_type in enumerate(task_types)
    ]
    (model_dir / "selected.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_id": "deepseek-v4-pro",
                        "repository": "example/deepseek",
                        "output": "deepseek-v4-pro/selected.jsonl",
                        "confidence": "high",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    records, _ = load_behavior_records(tmp_path)
    cards = build_behavior_profile_cards(records)

    assert len(cards) == 5
    assert cards[0].task_type == "all_tasks"


def test_selects_balanced_clean_embedding_tranche(tmp_path):
    records = []
    for index in range(6):
        records.append(
            BehaviorRecord(
                id=f"clean-{index}", model_id="deepseek-v4-pro", source_id="source",
                trajectory_id=str(index), sample_kind="response",
                task_type="coding" if index < 4 else "reasoning_math", outcome="success",
                confidence=0.9, persona_contaminated=False, observed_only=False,
                tool_call_count=0, assistant_turns=1, user_turns=1,
                behavior_tags=("verification_oriented",), task_excerpt="task",
                response_excerpt="observable response" * 20,
                embedding_text="embedding", content_hash=f"hash-{index}",
            )
        )
    records.append(
        BehaviorRecord(
            id="persona", model_id="gpt-5.6-luna", source_id="source",
            trajectory_id="persona", sample_kind="response", task_type="coding",
            outcome="unknown", confidence=0.5, persona_contaminated=True,
            observed_only=False, tool_call_count=0, assistant_turns=1, user_turns=1,
            behavior_tags=("plain_response",), task_excerpt="task",
            response_excerpt="response", embedding_text="embedding", content_hash="persona-hash",
        )
    )

    selected = select_behavior_evidence_records(records, samples_per_model=4)

    assert len(selected) == 4
    assert {record.model_id for record in selected} == {"deepseek-v4-pro"}
    assert {record.task_type for record in selected} == {"coding", "reasoning_math"}
