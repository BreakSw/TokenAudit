from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from typing import Any

from audit_core.config import AuditConfig
from audit_core.utils import log_event

from .llm import AgentOutputError, call_json_agent


class GroundTruthCuratorAgent:
    name = "GroundTruthCuratorAgent"

    def run(self, *, config: AuditConfig, evidence: dict[str, Any]) -> dict[str, Any]:
        required_keys = ("hard_constraints", "behavior_signatures", "discriminative_features", "limitations")
        try:
            output = call_json_agent(
                config=config,
                agent_name=self.name,
                temperature=0.1,
                max_tokens=3500,
                required_keys=required_keys,
                system_prompt=(
                    "You curate ground truth for a black-box model audit. Return JSON only. "
                    "Treat P0/P1 official specification evidence as hard evidence. Treat behavior samples as soft statistical observations. "
                    "Never turn writing style into an identity proof. Contrast claimed-model samples with other-model samples. "
                    "Do not invent capabilities or facts absent from evidence. Each item must cite evidence_ids. "
                    "Schema: {hard_constraints:[{feature,expected,evidence_ids,confidence}], "
                    "behavior_signatures:[{feature,expected,contrast,evidence_ids,confidence}], "
                    "discriminative_features:[{feature,why_discriminative,preferred_task_type}], "
                    "limitations:[string], recommended_dimensions:[string]}."
                ),
                payload={"retrieved_evidence": evidence},
            )
            output["ground_truth_source"] = "GroundTruthCuratorAgent"
        except AgentOutputError as primary_error:
            output = self._recover(config=config, evidence=evidence, primary_error=primary_error)
        return _attach_ground_truth_metadata(output, evidence)

    def _recover(
        self,
        *,
        config: AuditConfig,
        evidence: dict[str, Any],
        primary_error: AgentOutputError,
    ) -> dict[str, Any]:
        recovery_agent = "GroundTruthRecoveryAgent"
        required_keys = ("hard_constraints", "behavior_signatures", "discriminative_features", "limitations")
        log_event(
            "deep_ground_truth_recovery_start",
            {
                "agent": self.name,
                "recovery_agent": recovery_agent,
                "reason": type(primary_error).__name__,
            },
        )
        try:
            output = call_json_agent(
                config=config,
                agent_name=recovery_agent,
                temperature=0.0,
                max_tokens=2400,
                required_keys=required_keys,
                system_prompt=(
                    "Rebuild a compact evidence-grounded baseline after a malformed curator response. "
                    "Return exactly one JSON object with no markdown, explanation, or chain-of-thought. "
                    "Use only the supplied evidence. P0/P1 specifications are hard evidence; behavior rows are soft observations. "
                    "Every evidence-derived item must retain evidence_ids. Required schema: "
                    "{hard_constraints:[{feature,expected,evidence_ids,confidence}],"
                    "behavior_signatures:[{feature,expected,contrast,evidence_ids,confidence}],"
                    "discriminative_features:[{feature,why_discriminative,preferred_task_type}],"
                    "limitations:[string],recommended_dimensions:[string]}."
                ),
                payload=_compact_ground_truth_recovery_payload(evidence),
            )
            output["ground_truth_source"] = recovery_agent
            log_event(
                "deep_ground_truth_recovery_end",
                {
                    "agent": self.name,
                    "recovery_agent": recovery_agent,
                    "status": "success",
                    "method": "recovery_agent",
                },
            )
            return output
        except Exception as recovery_error:
            output = _deterministic_ground_truth(evidence)
            log_event(
                "deep_ground_truth_recovery_end",
                {
                    "agent": self.name,
                    "recovery_agent": recovery_agent,
                    "status": "success",
                    "method": "deterministic_evidence_fallback",
                    "recovery_failure": type(recovery_error).__name__,
                },
            )
            return output


def _attach_ground_truth_metadata(output: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    output["retrieval"] = {
        key: evidence.get(key)
        for key in (
            "declared_model_id",
            "knowledge_model_id",
            "spec_model_id",
            "behavior_model_id",
            "baseline_kind",
            "baseline_reason",
            "collections",
        )
    }
    output["evidence_counts"] = {
        "spec": len(evidence.get("spec_evidence", [])),
        "claimed_behavior": len(evidence.get("claimed_behavior", [])),
        "contrast_behavior": len(evidence.get("contrast_behavior", [])),
    }
    output["coverage"] = _coverage(output["evidence_counts"])
    return output


class ProbeDesignerAgent:
    name = "ProbeDesignerAgent"

    def run(
        self,
        *,
        config: AuditConfig,
        ground_truth: dict[str, Any],
        round_index: int,
        question_count: int,
        previous_rounds: list[dict[str, Any]],
        previous_prompts: list[str],
    ) -> list[dict[str, Any]]:
        payload = {
            "round": round_index,
            "question_count": question_count,
            "ground_truth": _bounded_ground_truth(ground_truth),
            "previous_round_summaries": [_round_summary(item) for item in previous_rounds],
            "previous_prompts": previous_prompts[-18:],
        }
        output = call_json_agent(
            config=config,
            agent_name=self.name,
            temperature=0.45,
            max_tokens=4200,
            required_keys=("probes",),
            system_prompt=(
                "Design NEW black-box audit probes from the supplied evidence. Return JSON only. "
                "Create exactly question_count probes. Do not ask the model to state its name. Do not copy dataset tasks verbatim. "
                "Round 1 covers distinct high-value capabilities; later rounds target weak, contradictory, or uncovered evidence. "
                "Every probe must be solvable without private tools unless its task explicitly requests a tool-call plan. "
                "Every probe needs at least one machine-checkable constraint using only: min_length, max_length, contains_any, "
                "contains_all, not_contains, json_keys, regex. Avoid brittle checks for prose. "
                "Schema: {probes:[{dimension,prompt,why_discriminative,invariants:[string],reference_facts:[string],"
                "rubric:[string],objective_checks:[{type,value?,values?}],max_tokens:int}]}"
            ),
            payload=payload,
        )
        probes = output.get("probes")
        if not isinstance(probes, list) or len(probes) != question_count:
            raise AgentOutputError(f"{self.name} must return exactly {question_count} probes")
        normalized: list[dict[str, Any]] = []
        for index, probe in enumerate(probes, start=1):
            if not isinstance(probe, dict) or not str(probe.get("prompt") or "").strip():
                raise AgentOutputError(f"{self.name} returned an empty probe")
            prompt = str(probe["prompt"]).strip()
            if any(_too_similar(prompt, old) for old in previous_prompts):
                raise AgentOutputError(f"{self.name} repeated a previous-round probe")
            normalized.append(
                {
                    "probe_group_id": f"r{round_index}-p{index}",
                    "dimension": str(probe.get("dimension") or "model_behavior")[:64],
                    "prompt": prompt,
                    "why_discriminative": str(probe.get("why_discriminative") or ""),
                    "invariants": _string_list(probe.get("invariants")),
                    "reference_facts": _string_list(probe.get("reference_facts")),
                    "rubric": _string_list(probe.get("rubric")),
                    "objective_checks": _checks(probe.get("objective_checks")),
                    # Keep enough room for reasoning models without making a
                    # 100K reservation that credit-based relays may reject.
                    "max_tokens": _target_output_budget(probe.get("max_tokens")),
                }
            )
        return normalized


class FuzzAgent:
    name = "FuzzAgent"

    def run_parallel(self, *, config: AuditConfig, probes: list[dict[str, Any]], round_index: int) -> list[dict[str, Any]]:
        with ThreadPoolExecutor(max_workers=min(3, len(probes)), thread_name_prefix="fuzz-agent") as executor:
            groups = list(executor.map(lambda probe: self._run_one(config, probe, round_index), probes))
        groups.sort(key=lambda item: item["probe_group_id"])
        return groups

    def _run_one(self, config: AuditConfig, probe: dict[str, Any], round_index: int) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                output = call_json_agent(
                    config=config,
                    agent_name=self.name,
                    temperature=0.72,
                    max_tokens=2400,
                    required_keys=("variants",),
                    system_prompt=(
                        "Generate exactly three semantically equivalent variants of one audit probe. Return JSON only. "
                        "Variant types must be paraphrase, distractor, and boundary. Preserve every invariant and difficulty. "
                        "Do not reveal reference facts, hints, answers, model names, dataset names, or audit intent. "
                        "The three prompts must be materially different in surface form. "
                        "Schema: {variants:[{variant_type,prompt}]}"
                    ),
                    payload={
                        "round": round_index,
                        "original_prompt": probe["prompt"],
                        "invariants": probe.get("invariants", []),
                        "attempt": attempt + 1,
                        "previous_error": str(last_error) if last_error else None,
                    },
                )
                variants = output.get("variants")
                if not isinstance(variants, list) or len(variants) != 3:
                    raise AgentOutputError("FuzzAgent must return exactly three variants")
                prompts = [str(item.get("prompt") or "").strip() for item in variants if isinstance(item, dict)]
                if len(prompts) != 3 or any(not prompt for prompt in prompts) or len(set(prompts)) != 3:
                    raise AgentOutputError("FuzzAgent returned empty or duplicate variants")
                normalized = []
                expected_types = ("paraphrase", "distractor", "boundary")
                for index, (item, prompt) in enumerate(zip(variants, prompts, strict=True), start=1):
                    variant_type = str(item.get("variant_type") or expected_types[index - 1]).casefold()
                    normalized.append(
                        {
                            "variant_id": f"{probe['probe_group_id']}-v{index}",
                            "variant_type": variant_type,
                            "prompt": prompt,
                        }
                    )
                return {**probe, "variants": normalized}
            except Exception as exc:
                last_error = exc
        assert last_error is not None
        raise last_error


class AuditJudgeAgent:
    name = "AuditJudgeAgent"

    def run(self, *, config: AuditConfig, ground_truth: dict[str, Any], groups: list[dict[str, Any]], responses: list[dict[str, Any]]) -> dict[str, Any]:
        required_keys = ("semantic_score", "ground_truth_alignment_score", "group_scores")
        try:
            output = call_json_agent(
                config=config,
                agent_name=self.name,
                temperature=0.05,
                max_tokens=4200,
                required_keys=required_keys,
                system_prompt=(
                    "Blindly judge target responses against the supplied rubrics and evidence. Return JSON only. "
                    "Do not infer identity from tone or a self-reported model name. Penalize factual errors, incomplete reasoning, "
                    "failure to follow constraints, and contradictions with hard evidence. Behavior samples are soft evidence only. "
                    "Score 0..100. Schema: {semantic_score:number,ground_truth_alignment_score:number,"
                    "group_scores:[{probe_group_id,semantic_score,ground_truth_alignment_score,reasons:[string]}],"
                    "critical_contradictions:[string],notes:[string]}."
                ),
                payload={
                    "ground_truth": _bounded_ground_truth(ground_truth),
                    "probe_groups": _groups_for_judge(groups),
                    "target_responses": _responses_for_judge(responses),
                },
            )
        except Exception as primary_error:
            log_event(
                "deep_judge_recovery_start",
                {
                    "agent": self.name,
                    "recovery_agent": "AuditJudgeRecoveryAgent",
                    "reason": type(primary_error).__name__,
                },
            )
            try:
                output = call_json_agent(
                    config=config,
                    agent_name="AuditJudgeRecoveryAgent",
                    temperature=0.0,
                    max_tokens=2600,
                    required_keys=required_keys,
                    system_prompt=(
                        "The primary audit judge returned malformed output. Re-evaluate the compact evidence independently. "
                        "Return one JSON object only, without analysis, markdown, or chain-of-thought. Do not infer model identity "
                        "from names or style. Score 0..100. Required schema: {semantic_score:number,"
                        "ground_truth_alignment_score:number,group_scores:[{probe_group_id,semantic_score,"
                        "ground_truth_alignment_score,reasons:[string]}],critical_contradictions:[string],notes:[string]}."
                    ),
                    payload=_compact_audit_recovery_payload(ground_truth, groups, responses),
                )
                output["recovered_by"] = "AuditJudgeRecoveryAgent"
                log_event(
                    "deep_judge_recovery_end",
                    {
                        "agent": self.name,
                        "recovery_agent": "AuditJudgeRecoveryAgent",
                        "status": "success",
                    },
                )
            except Exception as recovery_error:
                log_event(
                    "deep_judge_recovery_end",
                    {
                        "agent": self.name,
                        "recovery_agent": "AuditJudgeRecoveryAgent",
                        "status": "error",
                        "reason": type(recovery_error).__name__,
                    },
                )
                raise recovery_error from primary_error
        output["semantic_score"] = _score(output.get("semantic_score"))
        output["ground_truth_alignment_score"] = _score(output.get("ground_truth_alignment_score"))
        return output


class BehaviorJudgeAgent:
    name = "BehaviorJudgeAgent"

    def run(self, *, config: AuditConfig, evidence: dict[str, Any], responses: list[dict[str, Any]]) -> dict[str, Any]:
        output = call_json_agent(
            config=config,
            agent_name=self.name,
            temperature=0.05,
            max_tokens=3200,
            required_keys=("behavior_score", "claimed_similarity", "strongest_contrast_similarity"),
            system_prompt=(
                "Compare observable target behavior with claimed-model samples and contrast-model samples. Return JSON only. "
                "Use task handling, verification, correction, tool planning and failure modes; writing style alone is weak evidence. "
                "A generic strong answer that matches all models has low discriminative value. Persona-contaminated rows are absent. "
                "Score 0..100. Schema: {behavior_score:number,claimed_similarity:number,strongest_contrast_similarity:number,"
                "similarity_margin:number,discriminative_observations:[string],weak_or_generic_signals:[string],limitations:[string]}."
            ),
            payload={
                "claimed_behavior": evidence.get("claimed_behavior", []),
                "contrast_behavior": evidence.get("contrast_behavior", []),
                "target_responses": _responses_for_judge(responses),
            },
        )
        for key in ("behavior_score", "claimed_similarity", "strongest_contrast_similarity"):
            output[key] = _score(output.get(key))
        output["similarity_margin"] = round(
            output["claimed_similarity"] - output["strongest_contrast_similarity"], 2
        )
        return output


class ConsistencyJudgeAgent:
    name = "ConsistencyJudgeAgent"

    def run(self, *, config: AuditConfig, groups: list[dict[str, Any]], responses: list[dict[str, Any]]) -> dict[str, Any]:
        output = call_json_agent(
            config=config,
            agent_name=self.name,
            temperature=0.05,
            max_tokens=3000,
            required_keys=("consistency_score", "group_consistency", "routing_instability_suspected"),
                system_prompt=(
                    "Evaluate semantic consistency across three equivalent fuzz variants per probe. Return JSON only. "
                    "Compare correctness, reasoning approach, constraint following and capability level; surface wording may differ. "
                    "The input contains only successfully returned answers. Never penalize missing variants caused by transport failures; "
                    "judge consistency only from the available answers and state limited coverage in routing_evidence when applicable. "
                    "Flag routing instability only when capability or behavior changes materially across equivalent prompts. "
                "All consistency scores must use the 0..100 scale, never 0..1. "
                "Schema: {consistency_score:number,group_consistency:[{probe_group_id,score,reasons:[string]}],"
                "routing_instability_suspected:boolean,routing_evidence:[string]}."
            ),
            payload={"probe_groups": _groups_for_judge(groups), "target_responses": _responses_for_judge(responses)},
        )
        output = _normalize_consistency_output(output)
        return output


class RedTeamReviewerAgent:
    name = "RedTeamReviewerAgent"

    def run(self, *, config: AuditConfig, rounds: list[dict[str, Any]], score: dict[str, Any], limitations: list[str]) -> dict[str, Any]:
        return call_json_agent(
            config=config,
            agent_name=self.name,
            temperature=0.12,
            max_tokens=2400,
            required_keys=("material_alternative_explanations", "should_cap_confidence", "review_conclusion"),
            system_prompt=(
                "Act as a skeptical reviewer of a black-box relay-model audit. Return JSON only. "
                "Look for alternative explanations: gateway prompt rewriting, truncation, temperature, protocol conversion, rate limits, "
                "dynamic routing, weak knowledge coverage, contaminated behavior data, and ambiguous probes. "
                "Do not change the numeric score. Schema: {material_alternative_explanations:[string],"
                "should_cap_confidence:boolean,confidence_cap:number,unresolved_contradictions:[string],review_conclusion:string}."
            ),
            payload={"round_summaries": [_round_summary(item) for item in rounds], "deterministic_score": score, "limitations": limitations},
        )


class FinalDecisionAgent:
    name = "FinalDecisionAgent"

    def run(
        self,
        *,
        config: AuditConfig,
        score: dict[str, Any],
        red_team: dict[str, Any],
        ground_truth: dict[str, Any],
    ) -> dict[str, Any]:
        output = call_json_agent(
            config=config,
            agent_name=self.name,
            temperature=0.05,
            max_tokens=2600,
            required_keys=("overall_conclusion", "evidence_for", "evidence_against", "risk_warnings"),
                system_prompt=(
                    "Explain a deterministic black-box audit result in Simplified Chinese. Return JSON only. "
                "Every human-readable string in every field and list MUST be Simplified Chinese; do not output English prose. "
                "You may not alter total_score, band, component scores or weights. Do not claim cryptographic identity proof. "
                    "Use wording such as consistent or inconsistent with the declared baseline. Respect proxy-baseline disclosures. "
                    "When locked_score.network_unstable is true, explicitly warn that some questions had no answer because the network "
                    "was unstable, that only successful answers were scored, and that confidence was reduced. "
                "Schema: {overall_conclusion:string,evidence_for:[string],evidence_against:[string],"
                "risk_warnings:[string],usage_suggestions:[string],confidence_explanation:string}."
            ),
            payload={
                "locked_score": score,
                "red_team_review": red_team,
                "baseline": ground_truth.get("retrieval", {}),
                "coverage": ground_truth.get("coverage"),
                "limitations": ground_truth.get("limitations", []),
                "output_language": "zh-CN",
            },
        )
        output["total_score"] = score["total_score"]
        output["band"] = score["band"]
        output["confidence"] = score["confidence"]
        return output


def run_parallel_judges(
    *,
    config: AuditConfig,
    ground_truth: dict[str, Any],
    evidence: dict[str, Any],
    groups: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="deep-judge") as executor:
        audit_future = executor.submit(AuditJudgeAgent().run, config=config, ground_truth=ground_truth, groups=groups, responses=responses)
        behavior_future = executor.submit(BehaviorJudgeAgent().run, config=config, evidence=evidence, responses=responses)
        consistency_future = executor.submit(ConsistencyJudgeAgent().run, config=config, groups=groups, responses=responses)
        return audit_future.result(), behavior_future.result(), consistency_future.result()


def _compact_ground_truth_recovery_payload(evidence: dict[str, Any]) -> dict[str, Any]:
    def compact(rows: Any, limit: int) -> list[dict[str, Any]]:
        if not isinstance(rows, list):
            return []
        return [
            {
                "id": row.get("id") or row.get("source_id"),
                "source_level": row.get("source_level"),
                "claim_type": row.get("claim_type"),
                "record_type": row.get("record_type"),
                "sample_kind": row.get("sample_kind"),
                "task_type": row.get("task_type"),
                "outcome": row.get("outcome"),
                "confidence": row.get("confidence"),
                "text": str(row.get("text") or "")[:650],
            }
            for row in rows[:limit]
            if isinstance(row, dict) and str(row.get("text") or "").strip()
        ]

    return {
        "declared_model_id": evidence.get("declared_model_id"),
        "baseline_kind": evidence.get("baseline_kind"),
        "baseline_reason": evidence.get("baseline_reason"),
        "spec_evidence": compact(evidence.get("spec_evidence"), 5),
        "claimed_behavior": compact(evidence.get("claimed_behavior"), 6),
        "contrast_behavior": compact(evidence.get("contrast_behavior"), 6),
    }


def _deterministic_ground_truth(evidence: dict[str, Any]) -> dict[str, Any]:
    """Build a conservative baseline from retrieved rows without adding facts."""

    spec_rows = _evidence_rows(evidence.get("spec_evidence"), 8)
    claimed_rows = _evidence_rows(evidence.get("claimed_behavior"), 10)
    contrast_rows = _evidence_rows(evidence.get("contrast_behavior"), 10)
    hard_spec_rows = [
        row for row in spec_rows if str(row.get("source_level") or "").strip().upper() in {"P0", "P1"}
    ]

    hard_constraints = [
        {
            "feature": str(row.get("claim_type") or row.get("task_type") or "retrieved_specification")[:120],
            "expected": str(row.get("text") or "")[:900],
            "evidence_ids": _evidence_ids(row),
            "confidence": _evidence_confidence(row, default=0.75),
        }
        for row in hard_spec_rows
    ]

    behavior_signatures: list[dict[str, Any]] = []
    for index, row in enumerate(claimed_rows):
        contrast = _matching_contrast(row, contrast_rows, index)
        evidence_ids = _evidence_ids(row)
        if contrast:
            evidence_ids.extend(item for item in _evidence_ids(contrast) if item not in evidence_ids)
        behavior_signatures.append(
            {
                "feature": str(
                    row.get("task_type") or row.get("sample_kind") or row.get("record_type") or "observed_behavior"
                )[:120],
                "expected": str(row.get("text") or "")[:900],
                "contrast": str((contrast or {}).get("text") or "")[:700],
                "evidence_ids": evidence_ids,
                "confidence": _evidence_confidence(row, default=0.6),
            }
        )

    discriminative_features: list[dict[str, Any]] = []
    seen_features: set[str] = set()
    secondary_spec_features = [
        {
            "feature": str(row.get("claim_type") or row.get("task_type") or "secondary_specification")[:120],
            "why_discriminative": str(row.get("text") or "")[:700],
        }
        for row in spec_rows
        if row not in hard_spec_rows
    ]
    for item in [*hard_constraints, *behavior_signatures, *secondary_spec_features]:
        feature = str(item.get("feature") or "").strip()
        key = feature.casefold()
        if not feature or key in seen_features:
            continue
        seen_features.add(key)
        discriminative_features.append(
            {
                "feature": feature,
                "why_discriminative": "该特征直接来自检索证据，应通过可重复的黑盒任务验证。",
                "preferred_task_type": feature,
            }
        )
        if len(discriminative_features) >= 10:
            break

    dimensions = list(
        dict.fromkeys(
            str(row.get("task_type") or row.get("claim_type") or "").strip()
            for row in [*spec_rows, *claimed_rows]
            if str(row.get("task_type") or row.get("claim_type") or "").strip()
        )
    )[:10]
    limitations = [
        "审计者模型未返回可解析的 Ground Truth；当前基线由检索证据确定性恢复。",
        "行为样本仅属于统计性软证据，不能单独证明模型身份。",
    ]
    if evidence.get("baseline_kind") not in (None, "exact"):
        limitations.append(str(evidence.get("baseline_reason") or "当前使用的是代理基线，而非精确型号基线。")[:500])
    if not hard_spec_rows:
        limitations.append("未检索到 P0/P1 规格证据，不能建立硬能力约束。")
    if not claimed_rows:
        limitations.append("未检索到宣称模型行为样本，行为判别能力有限。")

    return {
        "hard_constraints": hard_constraints,
        "behavior_signatures": behavior_signatures,
        "discriminative_features": discriminative_features,
        "limitations": limitations,
        "recommended_dimensions": dimensions,
        "ground_truth_source": "deterministic_evidence_fallback",
    }


def _evidence_rows(value: Any, limit: int) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [
        row
        for row in value[:limit]
        if isinstance(row, dict) and str(row.get("text") or "").strip()
    ]


def _evidence_ids(row: dict[str, Any]) -> list[str]:
    value = row.get("id") or row.get("source_id")
    return [str(value)] if value not in (None, "") else []


def _evidence_confidence(row: dict[str, Any], *, default: float) -> float:
    try:
        value = float(row.get("confidence"))
    except (TypeError, ValueError):
        value = default
    if value > 1:
        value /= 100
    return round(max(0.0, min(1.0, value)), 3)


def _matching_contrast(
    claimed: dict[str, Any],
    contrast_rows: list[dict[str, Any]],
    fallback_index: int,
) -> dict[str, Any] | None:
    task_type = str(claimed.get("task_type") or "").casefold()
    if task_type:
        for row in contrast_rows:
            if str(row.get("task_type") or "").casefold() == task_type:
                return row
    if contrast_rows:
        return contrast_rows[fallback_index % len(contrast_rows)]
    return None


def _coverage(counts: dict[str, int]) -> float:
    spec = min(1.0, counts.get("spec", 0) / 5)
    claimed = min(1.0, counts.get("claimed_behavior", 0) / 8)
    contrast = min(1.0, counts.get("contrast_behavior", 0) / 8)
    return round(spec * 0.5 + claimed * 0.35 + contrast * 0.15, 4)


def _score(value: Any) -> float:
    try:
        return round(max(0.0, min(100.0, float(value))), 2)
    except Exception:
        return 0.0


def _normalize_consistency_output(output: dict[str, Any]) -> dict[str, Any]:
    groups = output.get("group_consistency")
    group_rows = groups if isinstance(groups, list) else []
    raw_values: list[float] = []
    for row in group_rows:
        if isinstance(row, dict):
            try:
                raw_values.append(float(row.get("score")))
            except (TypeError, ValueError):
                pass
    try:
        raw_overall = float(output.get("consistency_score"))
    except (TypeError, ValueError):
        raw_overall = 0.0
    fractional_scale = (
        0.0 <= raw_overall <= 1.0
        and bool(raw_values)
        and all(0.0 <= value <= 1.0 for value in raw_values)
        and any(0.0 < value < 1.0 for value in [raw_overall, *raw_values])
    )
    multiplier = 100.0 if fractional_scale else 1.0
    output["consistency_score"] = _score(raw_overall * multiplier)
    for row in group_rows:
        if isinstance(row, dict):
            try:
                row["score"] = _score(float(row.get("score")) * multiplier)
            except (TypeError, ValueError):
                row["score"] = 0.0
    return output


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item)[:800] for item in value if str(item).strip()]


def _checks(value: Any) -> list[dict[str, Any]]:
    supported = {"min_length", "max_length", "contains_any", "contains_all", "not_contains", "json_keys", "regex"}
    checks = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and str(item.get("type") or "").casefold() in supported:
                checks.append(item)
    return checks or [{"type": "min_length", "value": 40}]


def _target_output_budget(value: Any) -> int:
    # max_tokens is an upper bound, not a requested output length. Give the
    # audited model the full supported window so its natural answer is not
    # truncated; transport recovery may still reduce this after a real error.
    return 99_999


def _too_similar(left: str, right: str) -> bool:
    from difflib import SequenceMatcher

    return SequenceMatcher(None, " ".join(left.casefold().split()), " ".join(right.casefold().split())).ratio() >= 0.88


def _bounded_ground_truth(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "hard_constraints": value.get("hard_constraints", [])[:12],
        "behavior_signatures": value.get("behavior_signatures", [])[:12],
        "discriminative_features": value.get("discriminative_features", [])[:12],
        "limitations": value.get("limitations", [])[:10],
        "recommended_dimensions": value.get("recommended_dimensions", [])[:10],
        "retrieval": value.get("retrieval", {}),
        "coverage": value.get("coverage"),
    }


def _groups_for_judge(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "probe_group_id": group.get("probe_group_id"),
            "dimension": group.get("dimension"),
            "why_discriminative": group.get("why_discriminative"),
            "reference_facts": group.get("reference_facts", []),
            "rubric": group.get("rubric", []),
            "variants": group.get("variants", []),
        }
        for group in groups
    ]


def _responses_for_judge(responses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "probe_group_id": item.get("probe_group_id"),
            "variant_id": item.get("variant_id"),
            "ok": item.get("ok"),
            "status_code": item.get("status_code"),
            "response_text": str(item.get("response_text") or "")[:3500],
            "error": item.get("error"),
        }
        for item in responses
    ]


def _compact_audit_recovery_payload(
    ground_truth: dict[str, Any],
    groups: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "hard_constraints": [
            {
                "feature": item.get("feature"),
                "expected": str(item.get("expected") or "")[:600],
                "confidence": item.get("confidence"),
            }
            for item in ground_truth.get("hard_constraints", [])[:6]
            if isinstance(item, dict)
        ],
        "limitations": [str(item)[:400] for item in ground_truth.get("limitations", [])[:4]],
        "probe_groups": [
            {
                "probe_group_id": group.get("probe_group_id"),
                "dimension": group.get("dimension"),
                "rubric": [str(item)[:500] for item in group.get("rubric", [])[:4]],
                "reference_facts": [str(item)[:500] for item in group.get("reference_facts", [])[:4]],
            }
            for group in groups
        ],
        "target_responses": [
            {
                "probe_group_id": item.get("probe_group_id"),
                "variant_id": item.get("variant_id"),
                "ok": item.get("ok"),
                "status_code": item.get("status_code"),
                "response_text": str(item.get("response_text") or "")[:1600],
                "error": str(item.get("error") or "")[:300],
            }
            for item in responses
        ],
    }


def _round_summary(round_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "round": round_result.get("round"),
        "dimensions": [group.get("dimension") for group in round_result.get("probe_groups", [])],
        "objective_score": round_result.get("objective", {}).get("score"),
        "semantic_score": round_result.get("audit_judgement", {}).get("semantic_score"),
        "ground_truth_alignment_score": round_result.get("audit_judgement", {}).get("ground_truth_alignment_score"),
        "behavior_score": round_result.get("behavior_judgement", {}).get("behavior_score"),
        "consistency_score": round_result.get("consistency_judgement", {}).get("consistency_score"),
        "critical_contradictions": round_result.get("audit_judgement", {}).get("critical_contradictions", []),
        "routing_instability_suspected": round_result.get("consistency_judgement", {}).get("routing_instability_suspected", False),
    }
