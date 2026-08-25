from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from audit_core.agents.orchestrator_agent import OrchestratorInput
from audit_core.config import AuditConfig
from audit_core.utils import log_event, mask_token

from .agents import (
    FinalDecisionAgent,
    FuzzAgent,
    GroundTruthCuratorAgent,
    ProbeDesignerAgent,
    RedTeamReviewerAgent,
    run_parallel_judges,
)
from .knowledge import DeepKnowledgeGateway
from .services import ensure_target_transport_integrity, execute_variants, fuse_scores, verify_objective_checks


@dataclass(frozen=True)
class DeepAuditSettings:
    rounds: int = 2
    questions_per_round: int = 3
    variants_per_question: int = 3
    target_concurrency: int = 1
    adaptive_early_stop: bool = False

    def normalized(self) -> "DeepAuditSettings":
        return DeepAuditSettings(
            rounds=max(1, min(5, int(self.rounds))),
            questions_per_round=max(2, min(5, int(self.questions_per_round))),
            variants_per_question=3,
            target_concurrency=max(1, min(6, int(self.target_concurrency))),
            adaptive_early_stop=bool(self.adaptive_early_stop),
        )


class DeepAuditOrchestrator:
    name = "DeepAuditOrchestratorAgent"

    def run(
        self,
        *,
        config: AuditConfig,
        inp: OrchestratorInput,
        settings: DeepAuditSettings,
    ) -> dict[str, Any]:
        settings = settings.normalized()
        log_event(
            "phase_start",
            {
                "phase": "deep_orchestrator",
                "agent": self.name,
                "rounds": settings.rounds,
                "questions_per_round": settings.questions_per_round,
            },
        )
        gateway = DeepKnowledgeGateway()
        try:
            query = (
                "Find the most discriminative official capabilities, constraints, observable task behavior, "
                "verification patterns, correction patterns, tool-use patterns and failure modes for auditing "
                f"the declared model {inp.claimed_model}. Prefer features testable through an OpenAI-compatible chat API."
            )
            log_event("phase_start", {"phase": "deep_rag_retrieval", "agent": "GroundTruthCuratorAgent"})
            evidence = gateway.retrieve(model_id=inp.claimed_model, query=query)
            log_event(
                "deep_rag_evidence",
                {
                    "model": inp.claimed_model,
                    "spec_hits": len(evidence.get("spec_evidence", [])),
                    "claimed_behavior_hits": len(evidence.get("claimed_behavior", [])),
                    "contrast_behavior_hits": len(evidence.get("contrast_behavior", [])),
                    "spec_model_id": evidence.get("spec_model_id"),
                    "behavior_model_id": evidence.get("behavior_model_id"),
                },
            )
            ground_truth = GroundTruthCuratorAgent().run(config=config, evidence=evidence)
            log_event(
                "deep_ground_truth_ready",
                {
                    "coverage": ground_truth.get("coverage"),
                    "hard_constraints": len(ground_truth.get("hard_constraints", [])),
                    "behavior_signatures": len(ground_truth.get("behavior_signatures", [])),
                    "discriminative_features": [
                        str(item.get("feature") or "")[:160]
                        for item in ground_truth.get("discriminative_features", [])[:6]
                        if isinstance(item, dict)
                    ],
                    "limitations": len(ground_truth.get("limitations", [])),
                },
            )
            log_event(
                "phase_end",
                {
                    "phase": "deep_rag_retrieval",
                    "agent": "GroundTruthCuratorAgent",
                    "coverage": ground_truth.get("coverage"),
                    "evidence_counts": ground_truth.get("evidence_counts"),
                },
            )

            rounds: list[dict[str, Any]] = []
            previous_prompts: list[str] = []
            stopped_early = False
            for round_index in range(1, settings.rounds + 1):
                log_event("phase_start", {"phase": "deep_round", "round": round_index, "rounds": settings.rounds})
                probes = self._design_probes(
                    config=config,
                    ground_truth=ground_truth,
                    round_index=round_index,
                    question_count=settings.questions_per_round,
                    rounds=rounds,
                    previous_prompts=previous_prompts,
                )
                log_event(
                    "deep_probes_designed",
                    {
                        "round": round_index,
                        "count": len(probes),
                        "probes": [
                            {
                                "probe_group_id": probe.get("probe_group_id"),
                                "dimension": probe.get("dimension"),
                                "prompt": str(probe.get("prompt") or "")[:800],
                                "max_tokens": probe.get("max_tokens"),
                            }
                            for probe in probes
                        ],
                    },
                )
                groups = FuzzAgent().run_parallel(config=config, probes=probes, round_index=round_index)
                log_event(
                    "deep_fuzz_variants_ready",
                    {
                        "round": round_index,
                        "groups": len(groups),
                        "variants": sum(len(group.get("variants", [])) for group in groups),
                        "items": [
                            {
                                "probe_group_id": group.get("probe_group_id"),
                                "variant_id": variant.get("variant_id"),
                                "variant_type": variant.get("variant_type"),
                                "prompt": str(variant.get("prompt") or "")[:500],
                            }
                            for group in groups
                            for variant in group.get("variants", [])
                        ],
                    },
                )
                previous_prompts.extend(str(probe["prompt"]) for probe in probes)
                previous_prompts.extend(
                    str(variant["prompt"])
                    for group in groups
                    for variant in group.get("variants", [])
                )
                responses = execute_variants(
                    base_url=inp.token_base_url,
                    token=inp.audited_token,
                    model=inp.claimed_model,
                    round_index=round_index,
                    groups=groups,
                    timeout_s=config.request_timeout_s,
                    concurrency=settings.target_concurrency,
                )
                transport = ensure_target_transport_integrity(responses)
                scorable_responses = [response for response in responses if response.get("ok")]
                scorable_group_ids = {
                    str(response.get("probe_group_id"))
                    for response in scorable_responses
                }
                scorable_groups = [
                    group
                    for group in groups
                    if str(group.get("probe_group_id")) in scorable_group_ids
                ]
                objective = verify_objective_checks(scorable_groups, scorable_responses)
                audit_judgement, behavior_judgement, consistency_judgement = run_parallel_judges(
                    config=config,
                    ground_truth=ground_truth,
                    evidence=evidence,
                    groups=scorable_groups,
                    responses=scorable_responses,
                )
                log_event(
                    "deep_judges_completed",
                    {
                        "round": round_index,
                        "objective_score": objective.get("score"),
                        "semantic_score": audit_judgement.get("semantic_score"),
                        "ground_truth_alignment_score": audit_judgement.get("ground_truth_alignment_score"),
                        "behavior_score": behavior_judgement.get("behavior_score"),
                        "consistency_score": consistency_judgement.get("consistency_score"),
                        "routing_instability_suspected": consistency_judgement.get("routing_instability_suspected"),
                    },
                )
                round_result = {
                    "round": round_index,
                    "probe_groups": groups,
                    "responses": responses,
                    "transport": transport,
                    "objective": objective,
                    "audit_judgement": audit_judgement,
                    "behavior_judgement": behavior_judgement,
                    "consistency_judgement": consistency_judgement,
                }
                rounds.append(round_result)
                provisional = fuse_scores(rounds, coverage=float(ground_truth.get("coverage") or 0.0))
                log_event(
                    "phase_end",
                    {
                        "phase": "deep_round",
                        "round": round_index,
                        "rounds": settings.rounds,
                        "provisional_score": provisional["total_score"],
                        "band": provisional["band"],
                    },
                )
                if settings.adaptive_early_stop and _should_stop_early(rounds, provisional):
                    stopped_early = True
                    log_event(
                        "deep_early_stop",
                        {"round": round_index, "reason": "stable_high_confidence_result", "score": provisional["total_score"]},
                    )
                    break

            score = fuse_scores(rounds, coverage=float(ground_truth.get("coverage") or 0.0))
            red_team = RedTeamReviewerAgent().run(
                config=config,
                rounds=rounds,
                score=score,
                limitations=list(ground_truth.get("limitations") or []),
            )
            log_event(
                "deep_red_team_completed",
                {
                    "should_cap_confidence": red_team.get("should_cap_confidence"),
                    "confidence_cap": red_team.get("confidence_cap"),
                    "alternative_explanations": len(red_team.get("material_alternative_explanations", [])),
                    "unresolved_contradictions": len(red_team.get("unresolved_contradictions", [])),
                },
            )
            if red_team.get("should_cap_confidence"):
                cap = max(0.0, min(1.0, float(red_team.get("confidence_cap") or 0.65)))
                score["confidence"] = round(min(score["confidence"], cap), 4)
                score["confidence_capped_by_red_team"] = True
            decision = FinalDecisionAgent().run(
                config=config,
                score=score,
                red_team=red_team,
                ground_truth=ground_truth,
            )
            log_event(
                "deep_final_decision",
                {
                    "total_score": score.get("total_score"),
                    "band": score.get("band"),
                    "confidence": score.get("confidence"),
                    "valid_response_ratio": score.get("valid_response_ratio"),
                    "components": score.get("components"),
                },
            )
            report_markdown = build_deep_report_markdown(
                inp=inp,
                settings=settings,
                ground_truth=ground_truth,
                rounds=rounds,
                score=score,
                red_team=red_team,
                decision=decision,
                stopped_early=stopped_early,
            )
            log_event("phase_end", {"phase": "deep_orchestrator", "agent": self.name, "status": "success"})
            return {
                "base_info": {
                    "token_masked": mask_token(inp.audited_token),
                    "platform": inp.platform,
                    "claimed_model": inp.claimed_model,
                    "audit_mode": "deep",
                    "audit_time": inp.audit_time,
                },
                "deep_audit": {
                    "requested_rounds": settings.rounds,
                    "completed_rounds": len(rounds),
                    "questions_per_round": settings.questions_per_round,
                    "variants_per_question": settings.variants_per_question,
                    "stopped_early": stopped_early,
                },
                "ground_truth": ground_truth,
                "rounds": rounds,
                "score": score,
                "red_team_review": red_team,
                "overall": {
                    **decision,
                    "overall_conclusion": decision["overall_conclusion"],
                },
                "report_markdown": report_markdown,
            }
        finally:
            gateway.close()

    @staticmethod
    def _design_probes(
        *,
        config: AuditConfig,
        ground_truth: dict[str, Any],
        round_index: int,
        question_count: int,
        rounds: list[dict[str, Any]],
        previous_prompts: list[str],
    ) -> list[dict[str, Any]]:
        last_error: Exception | None = None
        for _ in range(2):
            try:
                return ProbeDesignerAgent().run(
                    config=config,
                    ground_truth=ground_truth,
                    round_index=round_index,
                    question_count=question_count,
                    previous_rounds=rounds,
                    previous_prompts=previous_prompts,
                )
            except Exception as exc:
                last_error = exc
        assert last_error is not None
        raise last_error


def _should_stop_early(rounds: list[dict[str, Any]], provisional: dict[str, Any]) -> bool:
    if len(rounds) < 2 or provisional.get("confidence", 0.0) < 0.9:
        return False
    previous = fuse_scores(rounds[:-1], coverage=1.0)
    return previous["band"] == provisional["band"] and abs(previous["total_score"] - provisional["total_score"]) < 3


def build_deep_report_markdown(
    *,
    inp: OrchestratorInput,
    settings: DeepAuditSettings,
    ground_truth: dict[str, Any],
    rounds: list[dict[str, Any]],
    score: dict[str, Any],
    red_team: dict[str, Any],
    decision: dict[str, Any],
    stopped_early: bool,
) -> str:
    lines = [
        "# TokenAudit 深度审计报告",
        "",
        "## 基本信息",
        "",
        f"- 平台：{inp.platform}",
        f"- 宣称模型：{inp.claimed_model}",
        f"- 审计时间：{inp.audit_time}",
        f"- 执行轮次：{len(rounds)} / {settings.rounds}",
        f"- 是否提前结束：{'是' if stopped_early else '否'}",
        f"- 规格知识基线：{ground_truth.get('retrieval', {}).get('spec_model_id') or ground_truth.get('retrieval', {}).get('knowledge_model_id')}",
        f"- 行为画像基线：{ground_truth.get('retrieval', {}).get('behavior_model_id') or ground_truth.get('retrieval', {}).get('knowledge_model_id')}",
        f"- 基线类型：{ground_truth.get('retrieval', {}).get('baseline_kind')}",
        f"- 知识覆盖率：{float(ground_truth.get('coverage') or 0):.1%}",
        "",
        "## 结论",
        "",
        f"- 总分：{score['total_score']:.2f} / 100",
        f"- 分档：{score['band']}",
        f"- 置信度：{score['confidence']:.1%}",
        f"- 有效响应：{score.get('scored_responses', 0)} / {score.get('total_responses', 0)}",
        f"- 网络状态：{'不稳定；未返回的问题不参与能力评分，且已降低置信度' if score.get('network_unstable') else '稳定'}",
        f"- 综合判断：{decision.get('overall_conclusion', '')}",
        "",
        "## 分项得分",
        "",
    ]
    for key, value in score.get("components", {}).items():
        lines.append(f"- {key}：{float(value):.2f}")
    lines.extend(("", "## Ground Truth 与知识证据摘要", ""))
    lines.extend(
        (
            f"- 规格证据：{ground_truth.get('evidence_counts', {}).get('spec', 0)} 条",
            f"- 宣称模型行为证据：{ground_truth.get('evidence_counts', {}).get('claimed_behavior', 0)} 条",
            f"- 对照模型行为证据：{ground_truth.get('evidence_counts', {}).get('contrast_behavior', 0)} 条",
            "",
            "### 硬约束",
            "",
        )
    )
    for constraint in ground_truth.get("hard_constraints", []):
        if not isinstance(constraint, dict):
            continue
        lines.extend(
            (
                f"- **{_md_inline(constraint.get('feature'))}**（置信度 {_md_inline(constraint.get('confidence'))}）：{_md_inline(constraint.get('expected'))}",
                f"  - 证据 ID：{', '.join(str(item) for item in constraint.get('evidence_ids', [])) or '无'}",
            )
        )
    lines.extend(("", "### 可观察行为特征", ""))
    for signature in ground_truth.get("behavior_signatures", []):
        if not isinstance(signature, dict):
            continue
        lines.extend(
            (
                f"- **{_md_inline(signature.get('feature'))}**：{_md_inline(signature.get('expected'))}",
                f"  - 对照：{_md_inline(signature.get('contrast'))}",
                f"  - 证据 ID：{', '.join(str(item) for item in signature.get('evidence_ids', [])) or '无'}",
            )
        )
    lines.extend(("", "### 基线限制", ""))
    lines.extend(f"- {_md_inline(item)}" for item in ground_truth.get("limitations", []))

    lines.extend(("", "## 完整审计流程", ""))
    for item in rounds:
        lines.extend(
            (
                f"### 第 {item['round']} 轮",
                "",
                f"- 客观约束：{item.get('objective', {}).get('score', 0)}",
                f"- 语义质量：{item.get('audit_judgement', {}).get('semantic_score', 0)}",
                f"- 官方基线符合度：{item.get('audit_judgement', {}).get('ground_truth_alignment_score', 0)}",
                f"- 行为差分：{item.get('behavior_judgement', {}).get('behavior_score', 0)}",
                f"- 模糊变体一致性：{item.get('consistency_judgement', {}).get('consistency_score', 0)}",
                "",
            )
        )
        responses = {
            str(response.get("variant_id")): response
            for response in item.get("responses", [])
            if isinstance(response, dict)
        }
        objective_groups = {
            str(group.get("probe_group_id")): group
            for group in item.get("objective", {}).get("groups", [])
            if isinstance(group, dict)
        }
        audit_groups = {
            str(group.get("probe_group_id")): group
            for group in item.get("audit_judgement", {}).get("group_scores", [])
            if isinstance(group, dict)
        }
        consistency_groups = {
            str(group.get("probe_group_id")): group
            for group in item.get("consistency_judgement", {}).get("group_consistency", [])
            if isinstance(group, dict)
        }
        for group in item.get("probe_groups", []):
            if not isinstance(group, dict):
                continue
            group_id = str(group.get("probe_group_id") or "unknown")
            lines.extend(
                (
                    f"#### 母题 {group_id} · {_md_inline(group.get('dimension'))}",
                    "",
                    f"- 判别目的：{_md_inline(group.get('why_discriminative'))}",
                    f"- 目标输出预算：{group.get('max_tokens', 0)} Token",
                    f"- 不变量：{'；'.join(_md_inline(value) for value in group.get('invariants', [])) or '无'}",
                    f"- 评分规则：{'；'.join(_md_inline(value) for value in group.get('rubric', [])) or '无'}",
                    "",
                    "**母题原文**",
                    "",
                    _md_block(group.get("prompt")),
                    "",
                )
            )
            objective_group = objective_groups.get(group_id, {})
            objective_by_variant = {
                str(row.get("variant_id")): row
                for row in objective_group.get("variant_results", [])
                if isinstance(row, dict)
            }
            for variant in group.get("variants", []):
                if not isinstance(variant, dict):
                    continue
                variant_id = str(variant.get("variant_id") or "unknown")
                response = responses.get(variant_id, {})
                objective_variant = objective_by_variant.get(variant_id, {})
                lines.extend(
                    (
                        f"##### 变体 {variant_id} · {_md_inline(variant.get('variant_type'))}",
                        "",
                        "**测试问题**",
                        "",
                        _md_block(variant.get("prompt")),
                        "",
                        f"- 调用结果：{'成功' if response.get('ok') else '失败'}",
                        f"- HTTP 状态：{response.get('status_code', 0)}",
                        f"- 耗时：{response.get('elapsed_ms', 0)} ms",
                        f"- 重试次数：{response.get('retry_count', 0)}",
                        f"- 客观检查得分：{objective_variant.get('score', 0)}",
                        f"- 错误：{_md_inline(response.get('error')) or '无'}",
                        "",
                        "**目标模型答案**",
                        "",
                        _md_block(response.get("response_text") or "（未返回可用的最终答案）"),
                        "",
                    )
                )
            audit_group = audit_groups.get(group_id, {})
            consistency_group = consistency_groups.get(group_id, {})
            lines.extend(
                (
                    f"- 本题语义得分：{audit_group.get('semantic_score', 0)}",
                    f"- 本题 Ground Truth 符合度：{audit_group.get('ground_truth_alignment_score', 0)}",
                    f"- 本题变体一致性：{consistency_group.get('score', 0)}",
                    f"- Judge 理由：{'；'.join(_md_inline(value) for value in audit_group.get('reasons', [])) or '无'}",
                    f"- 一致性理由：{'；'.join(_md_inline(value) for value in consistency_group.get('reasons', [])) or '无'}",
                    "",
                )
            )
        behavior = item.get("behavior_judgement", {})
        consistency = item.get("consistency_judgement", {})
        lines.extend(
            (
                "#### 本轮行为与路由判断",
                "",
                f"- 宣称模型相似度：{behavior.get('claimed_similarity', 0)}",
                f"- 最强对照模型相似度：{behavior.get('strongest_contrast_similarity', 0)}",
                f"- 相似度差值：{behavior.get('similarity_margin', 0)}",
                f"- 是否怀疑路由不稳定：{'是' if consistency.get('routing_instability_suspected') else '否'}",
                "",
            )
        )
        lines.extend(f"- 行为观察：{_md_inline(value)}" for value in behavior.get("discriminative_observations", []))
        lines.extend(f"- 路由证据：{_md_inline(value)}" for value in consistency.get("routing_evidence", []))
        lines.append("")

    lines.extend(("## RedTeam 反方复核", ""))
    lines.extend(f"- 替代解释：{_md_inline(item)}" for item in red_team.get("material_alternative_explanations", []))
    lines.extend(f"- 未解决矛盾：{_md_inline(item)}" for item in red_team.get("unresolved_contradictions", []))
    lines.extend(
        (
            f"- 是否限制置信度：{'是' if red_team.get('should_cap_confidence') else '否'}",
            f"- 置信度上限：{red_team.get('confidence_cap', '未设置')}",
            f"- 复核结论：{_md_inline(red_team.get('review_conclusion'))}",
            "",
        )
    )
    lines.extend(("## 支持证据", ""))
    lines.extend(f"- {item}" for item in decision.get("evidence_for", []))
    lines.extend(("", "## 反对证据与限制", ""))
    lines.extend(f"- {item}" for item in decision.get("evidence_against", []))
    lines.extend(f"- {item}" for item in red_team.get("material_alternative_explanations", []))
    lines.extend(
        (
            "",
            "> 本报告判断的是响应与宣称模型基线的一致程度，不构成模型身份的密码学证明。",
            "",
        )
    )
    return "\n".join(lines)


def _md_inline(value: Any) -> str:
    return " ".join(str(value or "").replace("|", "\\|").split())


def _md_block(value: Any) -> str:
    text = str(value or "").strip()
    return f"````text\n{text}\n````"
