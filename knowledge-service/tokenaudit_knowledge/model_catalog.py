from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal


@dataclass(frozen=True)
class ModelSpec:
    slug: str
    label: str
    family: str
    version: str
    aliases: tuple[str, ...]
    source_review_status: str


@dataclass(frozen=True)
class KnowledgeBaselineResolution:
    declared_model_id: str
    # Backward-compatible alias for the behavior baseline used by older callers.
    knowledge_model_id: str
    spec_model_id: str
    behavior_model_id: str
    baseline_kind: Literal["exact", "proxy"]
    baseline_reason: str | None = None


MODEL_SPECS: tuple[ModelSpec, ...] = (
    ModelSpec(
        slug="claude-fable-5",
        label="Claude Fable 5",
        family="claude",
        version="5",
        aliases=("Claude Fable 5", "Fable 5", "claude-fable-5"),
        source_review_status="APPROVE",
    ),
    ModelSpec(
        slug="claude-opus-4.6",
        label="Claude Opus 4.6",
        family="claude",
        version="4.6",
        aliases=("Claude Opus 4.6", "Opus 4.6", "claude-opus-4-6"),
        source_review_status="CONDITIONAL",
    ),
    ModelSpec(
        slug="deepseek-v4-pro",
        label="DeepSeek-V4-Pro",
        family="deepseek",
        version="4-pro",
        aliases=(
            "DeepSeek-V4-Pro",
            "DeepSeek V4 Pro",
            "DeepSeek-V4-Pro-Max",
            "DS-V4-Pro",
        ),
        source_review_status="APPROVE",
    ),
    ModelSpec(
        slug="glm-5.2",
        label="GLM-5.2",
        family="glm",
        version="5.2",
        aliases=("GLM-5.2", "GLM 5.2", "glm-5.2"),
        source_review_status="APPROVE",
    ),
    ModelSpec(
        slug="gpt-5.6-luna",
        label="GPT-5.6 Luna",
        family="gpt",
        version="5.6-luna",
        aliases=("GPT-5.6 Luna", "gpt-5.6-luna"),
        source_review_status="APPROVE",
    ),
    ModelSpec(
        slug="gpt-5.6-sol",
        label="GPT-5.6 Sol",
        family="gpt",
        version="5.6-sol",
        aliases=("GPT-5.6 Sol", "gpt-5.6-sol"),
        source_review_status="APPROVE",
    ),
    ModelSpec(
        slug="gpt-5.6-terra",
        label="GPT-5.6 Terra",
        family="gpt",
        version="5.6-terra",
        aliases=("GPT-5.6 Terra", "gpt-5.6-terra"),
        source_review_status="APPROVE",
    ),
    ModelSpec(
        slug="grok-5",
        label="Grok 5",
        family="grok",
        version="5",
        aliases=("Grok 5", "Grok-5", "grok-5"),
        source_review_status="HOLD",
    ),
    ModelSpec(
        slug="kimi-k3",
        label="Kimi K3",
        family="kimi",
        version="k3",
        aliases=("Kimi K3", "Kimi-K3", "kimi-k3"),
        source_review_status="APPROVE",
    ),
    ModelSpec(
        slug="qwen3-max",
        label="Qwen3-Max",
        family="qwen",
        version="3-max",
        aliases=("Qwen3-Max", "Qwen3 Max", "qwen3-max"),
        source_review_status="CONDITIONAL",
    ),
)


MODEL_BY_SLUG = {spec.slug: spec for spec in MODEL_SPECS}


def _normalized_model_key(value: str) -> str:
    key = value.strip().casefold().replace("_", "-")
    if "/" in key:
        key = key.rsplit("/", 1)[-1]
    key = re.sub(r"[^a-z0-9.-]+", "-", key).strip("-")
    return key


MODEL_ALIAS_TO_SLUG: dict[str, str] = {}
for _spec in MODEL_SPECS:
    MODEL_ALIAS_TO_SLUG[_normalized_model_key(_spec.slug)] = _spec.slug
    MODEL_ALIAS_TO_SLUG[_normalized_model_key(_spec.label)] = _spec.slug
    for _alias in _spec.aliases:
        MODEL_ALIAS_TO_SLUG[_normalized_model_key(_alias)] = _spec.slug


KNOWLEDGE_MODEL_ALIASES: dict[str, tuple[str, str, str]] = {
    "glm-5.3": (
        "glm-5.3",
        "glm-5.2",
        "GLM-5.3 暂无独立行为样本：规格证据使用 GLM-5.3，行为画像暂以 GLM-5.2 作为代理基线。",
    ),
}


def resolve_knowledge_baseline(model_id: str) -> KnowledgeBaselineResolution:
    declared_model_id = model_id.strip().lower()
    normalized = _normalized_model_key(model_id)
    canonical = MODEL_ALIAS_TO_SLUG.get(normalized, normalized)
    alias = KNOWLEDGE_MODEL_ALIASES.get(canonical)
    if alias:
        spec_model_id, behavior_model_id, reason = alias
        return KnowledgeBaselineResolution(
            declared_model_id=declared_model_id,
            knowledge_model_id=behavior_model_id,
            spec_model_id=spec_model_id,
            behavior_model_id=behavior_model_id,
            baseline_kind="proxy",
            baseline_reason=reason,
        )
    return KnowledgeBaselineResolution(
        declared_model_id=declared_model_id,
        knowledge_model_id=canonical,
        spec_model_id=canonical,
        behavior_model_id=canonical,
        baseline_kind="exact",
    )


def get_model_spec(slug: str) -> ModelSpec:
    resolved = resolve_knowledge_baseline(slug)
    try:
        return MODEL_BY_SLUG[resolved.knowledge_model_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported model slug: {slug}") from exc


def remaining_model_specs() -> tuple[ModelSpec, ...]:
    return tuple(spec for spec in MODEL_SPECS if spec.slug != "claude-fable-5")
