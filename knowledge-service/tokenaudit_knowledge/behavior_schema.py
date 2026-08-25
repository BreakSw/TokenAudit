from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BehaviorRecord:
    id: str
    model_id: str
    source_id: str
    trajectory_id: str
    sample_kind: str
    task_type: str
    outcome: str
    confidence: float
    persona_contaminated: bool
    observed_only: bool
    tool_call_count: int
    assistant_turns: int
    user_turns: int
    behavior_tags: tuple[str, ...]
    task_excerpt: str
    response_excerpt: str
    embedding_text: str
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["behavior_tags"] = list(self.behavior_tags)
        return result
