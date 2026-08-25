from __future__ import annotations

import json
import re
from typing import Any


def safe_json_loads(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def _json_candidates(text: str) -> list[str]:
    """Return plausible JSON objects without greedily joining separate objects."""

    candidates = [
        match.group(1).strip()
        for match in re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    ]
    # When a model emits a draft object followed by a corrected final object,
    # the last complete object is normally authoritative.
    candidates.extend(reversed(_balanced_objects(text)))

    # Some reasoning providers exhaust their output budget after producing an
    # almost complete object. This conservative repair only closes delimiters;
    # it never invents keys or values.
    truncated = _close_truncated_object(text)
    if truncated:
        candidates.append(truncated)

    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def _balanced_objects(text: str) -> list[str]:
    objects: list[str] = []
    start: int | None = None
    stack: list[str] = []
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if start is None:
            if char == "{":
                start = index
                stack = ["}"]
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "{[":
            stack.append("}" if char == "{" else "]")
        elif char in "}]":
            if not stack or char != stack[-1]:
                start = None
                stack = []
                in_string = False
                escaped = False
                continue
            stack.pop()
            if not stack:
                objects.append(text[start : index + 1].strip())
                start = None
    return objects


def _close_truncated_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None
    fragment = text[start:].strip()
    stack: list[str] = []
    in_string = False
    escaped = False
    for char in fragment:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "{[":
            stack.append("}" if char == "{" else "]")
        elif char in "}]":
            if not stack or char != stack[-1]:
                return None
            stack.pop()
    if not stack or len(fragment) > 200_000:
        return None
    if in_string:
        fragment += '"'
    fragment = re.sub(r",\s*$", "", fragment)
    return fragment + "".join(reversed(stack))


def _minor_json_repairs(candidate: str) -> list[str]:
    normalized_quotes = candidate.translate(str.maketrans({"“": '"', "”": '"'}))
    no_trailing_commas = re.sub(r",\s*([}\]])", r"\1", normalized_quotes)
    variants = [candidate, normalized_quotes, no_trailing_commas]
    return list(dict.fromkeys(variants))


def coerce_json_object(text: str) -> dict[str, Any]:
    for candidate in [text, *_json_candidates(text)]:
        for repaired in _minor_json_repairs(candidate):
            parsed = safe_json_loads(repaired)
            if isinstance(parsed, dict):
                return parsed

    return {"raw_text": text}
