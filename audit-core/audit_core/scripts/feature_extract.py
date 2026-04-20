from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class ResponseFeature:
    content_len: int
    has_markdown_code: bool
    mentions_model_name: bool
    mentions_thinking: bool
    contains_refusal: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_content(token_api_response: dict[str, Any]) -> str:
    data = token_api_response.get("response") or {}
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
        if isinstance(data.get("text"), str):
            return data["text"]
    return ""


def extract_features(token_api_response: dict[str, Any]) -> ResponseFeature:
    content = _extract_content(token_api_response)
    content_lower = content.lower()
    has_markdown_code = "```" in content
    mentions_model_name = bool(re.search(r"\b(model|gpt|claude|gemini|deepseek)\b", content_lower))
    mentions_thinking = "思考" in content or "thinking" in content_lower
    contains_refusal = bool(re.search(r"(cannot|can't|unable|抱歉|无法|不能)", content_lower))
    return ResponseFeature(
        content_len=len(content),
        has_markdown_code=has_markdown_code,
        mentions_model_name=mentions_model_name,
        mentions_thinking=mentions_thinking,
        contains_refusal=contains_refusal,
    )
