from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
PRIVATE_USE_RE = re.compile(r"[\uE000-\uF8FF]")

#预先定义要找什么事实
@dataclass(frozen=True)
class ClaimSpec:
    claim_id: str
    source_id: str
    claim_type: str
    predicate: str
    value: Any
    summary_zh: str
    evidence_pattern: str
    authority: float
    audit_relevance: float
    eligible_for_ground_truth: bool
    surface: str = "unspecified"
    fallback_contaminated: bool = False
    comparison_models: tuple[str, ...] = ()
    effective_from: str = ""
    quarantine_reason: str = ""


CLAIM_SPECS: tuple[ClaimSpec, ...] = (
    ClaimSpec(
        "fable5-model-id",
        "02-claude-docs-introduction",
        "model_identity",
        "api_model_id",
        "claude-fable-5",
        "Claude Fable 5 的官方 API 模型 ID 是 claude-fable-5。",
        r"(?:\| Claude Fable 5 \| `claude-fable-5` \|[^\n]+|Claude Fable 5\s+claude-fable-5\s+Anthropic's most capable widely released model[^\n]*)",
        1.0,
        0.25,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-context-output",
        "02-claude-docs-introduction",
        "hard_limit",
        "context_and_output_tokens",
        {"context_tokens": 1_000_000, "max_output_tokens": 128_000},
        "Claude Fable 5 默认支持 100 万 Token 上下文，单次最多输出 12.8 万 Token。",
        r"Context window and output:.*?1M token context window.*?128k output tokens per request\.",
        1.0,
        0.62,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-refusal-protocol",
        "02-claude-docs-introduction",
        "api_behavior",
        "classifier_refusal_response",
        {"http_status": 200, "stop_reason": "refusal", "is_error": False},
        "安全分类器拒绝请求时，Messages API 返回 HTTP 200，stop_reason 为 refusal，而不是 HTTP 错误。",
        r"When Claude Fable 5 declines a request, the Messages API returns.*?successful HTTP 200 response, not an error\..*?classifier declined the request\.",
        1.0,
        0.98,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-fallback-modes",
        "02-claude-docs-introduction",
        "fallback_behavior",
        "fallback_modes",
        ["server_side", "client_side", "manual"],
        "Fable 5 被拒绝后可通过服务端、客户端中间件或手工逻辑重试其他 Claude 模型。",
        r"A request that Claude Fable 5 refuses can usually be served by another Claude model\. There are three ways to retry:.*?Manual:.*?Fallback credit[^\n]*",
        1.0,
        0.96,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-refusal-billing",
        "02-claude-docs-introduction",
        "api_behavior",
        "refusal_billing",
        "not_billed_before_output",
        "在输出产生前被拒绝的 Fable 5 请求不计费；切换模型可通过 fallback credit 避免重复支付提示缓存费用。",
        r"You are not billed for a request that is refused before any output is generated\..*?avoid paying that cost twice\.",
        1.0,
        0.42,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-adaptive-thinking",
        "02-claude-docs-introduction",
        "reasoning_behavior",
        "adaptive_thinking",
        {"always_on": True, "disabled_parameter_supported": False, "control": "effort"},
        "Claude Fable 5 始终启用 Adaptive Thinking，不支持 thinking.disabled，应通过 effort 控制思考深度。",
        r"Claude Fable 5 and Claude Mythos 5 always have thinking enabled;.*?use the.*?effort.*?parameter\.",
        1.0,
        0.93,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-thinking-visibility",
        "02-claude-docs-introduction",
        "reasoning_behavior",
        "thinking_output",
        {"raw_chain_of_thought": False, "modes": ["summarized", "omitted"]},
        "Claude Fable 5 不返回原始思维链；thinking.display 只能返回摘要或省略内容。",
        r"The raw chain of thought is never returned.*?omitted.*?empty (?:`thinking`|thinking) field\.",
        1.0,
        0.88,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-supported-features",
        "02-claude-docs-introduction",
        "supported_feature",
        "supported_features",
        [
            "effort",
            "task_budgets",
            "memory_tool",
            "code_execution",
            "programmatic_tool_calling",
            "context_editing",
            "compaction",
            "vision",
        ],
        "Claude Fable 5 支持 effort、task budgets、memory、代码执行、程序化工具调用、上下文编辑、压缩和视觉。",
        r"At launch, Claude Fable 5 and Claude Mythos 5 support:.*?Vision[^\n]*",
        1.0,
        0.86,
        True,
        surface="claude_api",
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-opus-fallback",
        "03-anthropic-research",
        "fallback_behavior",
        "classifier_fallback_target",
        {
            "target": "claude-opus-4-8",
            "domains": ["cybersecurity", "biology_chemistry", "distillation"],
            "native_session_rate_lower_bound": 0.95,
        },
        "Fable 5 分类器检测到网络安全、生物化学或模型蒸馏风险时，可由 Opus 4.8 处理；官方早期数据称超过 95% 会话不触发 fallback。",
        r"When Fable’s classifiers detect a request related to cybersecurity, biology and chemistry, or distillation, the response is automatically handled by Claude Opus 4\.8 instead\..*?more than 95% of Fable sessions involve no fallback at all[^.]*\.",
        0.95,
        0.99,
        True,
        surface="claude_consumer_and_managed_fallback",
        comparison_models=("claude-opus-4-8", "claude-mythos-5"),
        effective_from="2026-06-09",
    ),
    ClaimSpec(
        "fable5-retention",
        "02-claude-docs-introduction",
        "data_policy",
        "data_retention_days",
        30,
        "Fable 5 要求 30 天数据保留且不支持零数据保留。",
        r"carry 30-day data retention and are not available under zero data retention",
        1.0,
        0.05,
        False,
        effective_from="2026-06-09",
        quarantine_reason="operational policy is not a model-behavior fingerprint",
    ),
    ClaimSpec(
        "fable5-long-horizon-marketing",
        "01-anthropic-fable",
        "performance_claim",
        "long_horizon_agentic_work",
        "days_at_a_time",
        "Anthropic 产品页宣称 Fable 5 可在 Agent Harness 中连续工作数日并执行规划、委派和自检。",
        r"Run Claude Fable 5 in an agent harness.*?checking its own work\.",
        0.55,
        0.76,
        False,
        comparison_models=("claude-opus-4-8",),
        quarantine_reason="official marketing claim lacks a reproducible harness and variance",
    ),
    ClaimSpec(
        "fable5-aa-intelligence",
        "04-artificial-analysis",
        "benchmark_result",
        "aa_intelligence_index",
        62,
        "Artificial Analysis 的带 Opus 4.8 fallback、Max Effort 配置给出 Intelligence Index 62。",
        r"scores 62 on the Artificial Analysis Intelligence Index[^.]*\.",
        0.75,
        0.72,
        False,
        fallback_contaminated=True,
        comparison_models=("claude-opus-4-8",),
        quarantine_reason="benchmark variant explicitly includes Opus 4.8 fallback and Max Effort",
    ),
    ClaimSpec(
        "fable5-aa-speed",
        "04-artificial-analysis",
        "performance_metric",
        "output_tokens_per_second",
        70.5,
        "Artificial Analysis 的混合配置测得约 70.5 输出 Token/秒。",
        r"generates output at 70\.5 tokens per second.*?77\.5 t/s\)\.",
        0.75,
        0.35,
        False,
        fallback_contaminated=True,
        quarantine_reason="single provider snapshot with fallback and no stored variance",
    ),
    ClaimSpec(
        "fable5-aa-ttft",
        "04-artificial-analysis",
        "performance_metric",
        "time_to_first_token_seconds",
        69.39,
        "Artificial Analysis 的混合配置测得 TTFT 69.39 秒。",
        r"has a time to first token \(TTFT\) of 69\.39s.*?2\.89s\)\.",
        0.75,
        0.35,
        False,
        fallback_contaminated=True,
        quarantine_reason="single provider snapshot with fallback and no stored variance",
    ),
    ClaimSpec(
        "fable5-japan-swebench",
        "05-japan-ai",
        "benchmark_result",
        "swe_bench_pro_percent",
        80.3,
        "JAPAN AI 二手资料列出 SWE-bench Pro 80.3%，但缺少已校验的官方图片表格和完整评测设置。",
        r"SWE-bench Proでは80\.3%.*?69\.2%.*?11ポイント以上[^。]*。",
        0.35,
        0.68,
        False,
        comparison_models=("claude-opus-4-8", "gpt-5.5", "gemini-3.1-pro"),
        quarantine_reason="secondary-language source and benchmark settings are not yet verified",
    ),
)


def _sha256(text: str | bytes) -> str:
    payload = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(payload).hexdigest()


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, text[match.end() :]


def _image_role(alt: str, heading: str) -> str:
    context = f"{alt} {heading}".lower()
    if any(word in context for word in ("benchmark", "evaluation", "table", "graph")):
        return "benchmark_image_pending_verification"
    if "logo" in context or not alt.strip():
        return "decorative_or_unlabelled_image"
    return "supporting_image_pending_review"


def _clean_source(
    source_id: str,
    text: str,
) -> tuple[dict[str, str], str, list[dict[str, Any]], list[dict[str, Any]]]:
    front_matter, body = _parse_front_matter(text)
    source_level = front_matter.get("priority", "")
    current_heading = ""
    output: list[str] = []
    assets: list[dict[str, Any]] = []
    dropped_sections: list[dict[str, Any]] = []
    dropping = False
    started = source_id != "05-japan-ai"

    exact_noise = {
        "Copy page",
        "Was this page helpful?",
        "Tap to unmute",
        "Claude547K subscribers",
        "NEW",
        "Add model from specific provider",
        "Reasoning models are indicated by a lightbulb icon",
        "Premium",
        "Log in K",
        "•",
        "01 /26",
    }

    for raw_line in body.splitlines():
        line = PRIVATE_USE_RE.sub("", raw_line).strip()
        line = line.replace("# Claude Claude Fable 5", "# Claude Fable 5")
        heading_match = HEADING_RE.match(line)
        if heading_match:
            title = heading_match.group(2).strip()
            current_heading = title
            if source_id == "05-japan-ai" and title == "Claude Fable 5とは":
                started = True
            if not started:
                continue
            if source_id == "01-anthropic-fable":
                dropping = title in {"Announcements", "Hear from our customers"}
            elif source_id == "03-anthropic-research":
                if title == "Related content":
                    dropped_sections.append(
                        {"source_id": source_id, "heading": title, "reason": "related content"}
                    )
                    break
                dropping = title == "Early feedback for Claude Fable 5"
            else:
                dropping = False
            if dropping:
                dropped_sections.append(
                    {"source_id": source_id, "heading": title, "reason": "marketing or duplicate section"}
                )
                continue

        if not started or dropping:
            continue

        for image_match in list(IMAGE_RE.finditer(line)):
            alt, url = image_match.groups()
            role = _image_role(alt, current_heading)
            asset_id = f"asset-{_sha256(url)[:16]}"
            assets.append(
                {
                    "asset_id": asset_id,
                    "source_id": source_id,
                    "source_level": source_level,
                    "heading": current_heading,
                    "alt": alt.strip(),
                    "url": url,
                    "role": role,
                    "embedding_eligible": False,
                }
            )
            replacement = ""
            if role == "benchmark_image_pending_verification":
                replacement = f"[BENCHMARK_IMAGE_PENDING_VERIFICATION: {alt or current_heading}]"
            line = line.replace(image_match.group(0), replacement)

        normalized = re.sub(r"\s+", " ", line).strip()
        plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", normalized).strip()
        if plain in exact_noise:
            continue
        if any(
            marker in normalized
            for marker in (
                "youtube.com/watch",
                "youtube-nocookie.com/channel",
                "twitter.com/intent/tweet",
                "linkedin.com/shareArticle",
                "uqid=",
            )
        ):
            continue
        if source_id == "04-artificial-analysis" and (
            re.fullmatch(r"\d+ of \d+ models", normalized)
            or normalized.startswith("Open Weights / ProprietaryReasoning")
            or normalized.startswith("CodingTool UsePrivate Dataset")
            or normalized.startswith("AnthropicMetaOpenAI")
        ):
            continue
        if source_id == "05-japan-ai" and normalized in {"目次", "【関連記事】"}:
            continue
        if not normalized:
            if output and output[-1] != "":
                output.append("")
            continue
        output.append(normalized)

    while output and not output[-1]:
        output.pop()
    return front_matter, "\n".join(output) + "\n", assets, dropped_sections


def _sections(
    *,
    source_id: str,
    source_level: str,
    source_url: str,
    clean_text: str,
) -> list[dict[str, Any]]:
    stack: list[str] = []
    section_title = "Preamble"
    section_lines: list[str] = []
    results: list[dict[str, Any]] = []

    def flush() -> None:
        nonlocal section_lines
        body = "\n".join(section_lines).strip()
        if not body:
            section_lines = []
            return
        heading_path = [*stack] if stack else [section_title]
        digest = _sha256(f"{source_id}|{'/'.join(heading_path)}|{body}")
        results.append(
            {
                "section_id": f"section-{digest[:20]}",
                "source_id": source_id,
                "source_level": source_level,
                "source_url": source_url,
                "heading_path": heading_path,
                "text": body,
                "characters": len(body),
                "fallback_contaminated": source_id == "04-artificial-analysis",
                "embedding_eligible": False,
            }
        )
        section_lines = []

    for line in clean_text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            flush()
            level = len(match.group(1))
            title = match.group(2).strip()
            stack[:] = stack[: level - 1]
            while len(stack) < level - 1:
                stack.append("Untitled")
            stack.append(title)
            section_title = title
            continue
        section_lines.append(line)
    flush()
    return results


def _find_evidence(clean_text: str, pattern: str) -> str:
    match = re.search(pattern, clean_text, re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError(f"Required evidence pattern was not found: {pattern}")
    return re.sub(r"\s+", " ", match.group(0)).strip()


def _build_claims(documents: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for spec in CLAIM_SPECS:
        document = documents[spec.source_id]
        evidence = _find_evidence(document["clean_text"], spec.evidence_pattern)
        claim = {
            "id": spec.claim_id,
            "record_type": "claim",
            "model_id": "claude-fable-5",
            "subject_model": "claude-fable-5",
            "comparison_models": list(spec.comparison_models),
            "claim_type": spec.claim_type,
            "predicate": spec.predicate,
            "value": spec.value,
            "summary_zh": spec.summary_zh,
            "evidence_quote": evidence,
            "source_id": spec.source_id,
            "source_level": document["front_matter"].get("priority", ""),
            "source_url": document["front_matter"].get("source_url", ""),
            "surface": spec.surface,
            "effective_from": spec.effective_from,
            "authority": spec.authority,
            "audit_relevance": spec.audit_relevance,
            "eligible_for_ground_truth": spec.eligible_for_ground_truth,
            "fallback_contaminated": spec.fallback_contaminated,
            "quarantine_reason": spec.quarantine_reason,
        }
        claim["content_hash"] = _sha256(
            json.dumps(claim, ensure_ascii=False, sort_keys=True)
        )
        claim["embedding_text"] = (
            f"模型：Claude Fable 5\n"
            f"事实类型：{spec.claim_type}\n"
            f"结论：{spec.summary_zh}\n"
            f"适用表面：{spec.surface}\n"
            f"原文证据：{evidence}"
        )
        claims.append(claim)
    return claims


def _build_attributes(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {claim["id"]: claim for claim in claims}
    specs = [
        {
            "id": "attr-fable5-refusal-protocol",
            "claim_type": "api_behavior",
            "title": "安全分类器拒绝协议",
            "source_claim_ids": ["fable5-refusal-protocol", "fable5-refusal-billing"],
            "watering_types": ["model_substitution", "api_contract_mismatch"],
            "expected_signal": "安全分类器触发时 HTTP 仍为 200，stop_reason=refusal，并返回分类器信息。",
            "contrast_signal": "普通错误通常返回非 2xx；不兼容中转层可能吞掉 stop_reason 或改写为错误。",
            "measurement": "检查原始响应状态码、stop_reason 和 stop_details；不得仅检查自然语言。",
            "test_config": "使用安全、非操作性的边界请求；至少 3 次，禁止生成攻击载荷。",
            "minimum_runs": 3,
            "discriminative_power": 0.90,
            "testability": 0.92,
            "stability": 0.86,
            "spoofability": 0.42,
            "estimated_cost": 0.20,
            "surface": "claude_api",
        },
        {
            "id": "attr-fable5-fallback-disambiguation",
            "claim_type": "fallback_behavior",
            "title": "官方 fallback 与中转站偷换模型区分",
            "source_claim_ids": ["fable5-fallback-modes", "fable5-opus-fallback"],
            "watering_types": ["dynamic_routing", "model_substitution"],
            "expected_signal": "只有分类器触发或显式配置 fallback 时才允许转由 Opus 4.8 处理，并应存在拒绝/切换信号。",
            "contrast_signal": "普通领域持续呈现 Opus 4.8 分布且无切换信号，才更像中转站动态替换。",
            "measurement": "将普通任务和安全边界任务分组，多次采样响应字段与能力分布，禁止把单次 fallback 判成掺水。",
            "test_config": "两组各至少 3 次；记录 surface、fallback 参数、stop_reason、返回模型字段和审计得分。",
            "minimum_runs": 6,
            "discriminative_power": 0.98,
            "testability": 0.80,
            "stability": 0.72,
            "spoofability": 0.38,
            "estimated_cost": 0.55,
            "surface": "mixed",
        },
        {
            "id": "attr-fable5-adaptive-thinking",
            "claim_type": "reasoning_behavior",
            "title": "Adaptive Thinking 强制开启",
            "source_claim_ids": ["fable5-adaptive-thinking"],
            "watering_types": ["reasoning_budget_reduction", "api_contract_mismatch"],
            "expected_signal": "thinking.disabled 不受支持，推理深度应由 effort 控制。",
            "contrast_signal": "接受并真实关闭 thinking，或完全忽略 effort 行为，可能表明接口/模型不匹配。",
            "measurement": "对 thinking.disabled 与多个 effort 值执行协议测试，比较错误字段和输出预算。",
            "test_config": "固定提示和采样参数，每个 effort 至少 3 次。",
            "minimum_runs": 9,
            "discriminative_power": 0.87,
            "testability": 0.95,
            "stability": 0.90,
            "spoofability": 0.50,
            "estimated_cost": 0.45,
            "surface": "claude_api",
        },
        {
            "id": "attr-fable5-thinking-visibility",
            "claim_type": "reasoning_behavior",
            "title": "思考内容可见性",
            "source_claim_ids": ["fable5-thinking-visibility"],
            "watering_types": ["api_contract_mismatch", "model_substitution"],
            "expected_signal": "不会返回原始思维链；thinking.display 仅支持 summarized 或 omitted。",
            "contrast_signal": "声称返回完整原始思维链，或不识别两种显示模式，可能是非目标接口。",
            "measurement": "检查 thinking block 结构和 display 模式，不能以模型自报名称评分。",
            "test_config": "同一推理题分别设置 summarized 与 omitted，各运行 3 次。",
            "minimum_runs": 6,
            "discriminative_power": 0.82,
            "testability": 0.94,
            "stability": 0.91,
            "spoofability": 0.54,
            "estimated_cost": 0.35,
            "surface": "claude_api",
        },
        {
            "id": "attr-fable5-tools",
            "claim_type": "supported_feature",
            "title": "复杂工具能力组合",
            "source_claim_ids": ["fable5-supported-features"],
            "watering_types": ["feature_restriction", "model_substitution"],
            "expected_signal": "支持 memory、code execution、programmatic tool calling、context editing、compaction 和 vision。",
            "contrast_signal": "只验证单次普通 function call 区分度不足；低价模型可能缺少组合式工具链。",
            "measurement": "构造多约束工具链并验证参数结构、依赖顺序、结果回填与自我修正。",
            "test_config": "每个测试生成 3 个模糊变体；至少两个独立工具属性失败才计入替换证据。",
            "minimum_runs": 6,
            "discriminative_power": 0.84,
            "testability": 0.78,
            "stability": 0.76,
            "spoofability": 0.44,
            "estimated_cost": 0.65,
            "surface": "claude_api",
        },
        {
            "id": "attr-fable5-context-output",
            "claim_type": "hard_limit",
            "title": "上下文和输出硬限制",
            "source_claim_ids": ["fable5-context-output"],
            "watering_types": ["context_truncation", "output_length_restriction"],
            "expected_signal": "默认 100 万 Token 上下文，单次最多输出 12.8 万 Token。",
            "contrast_signal": "中转站可能提前截断输入或设置更低输出上限，但单次短任务无法验证。",
            "measurement": "使用跨位置证据召回和渐进长度测试；将网关限制与模型限制分开记录。",
            "test_config": "先低成本分段递增，达到异常阈值后再做长上下文确认；至少 3 次。",
            "minimum_runs": 3,
            "discriminative_power": 0.75,
            "testability": 0.55,
            "stability": 0.85,
            "spoofability": 0.32,
            "estimated_cost": 0.95,
            "surface": "claude_api",
        },
    ]
    attributes: list[dict[str, Any]] = []
    for spec in specs:
        source_claims = [by_id[claim_id] for claim_id in spec["source_claim_ids"]]
        if not all(claim["eligible_for_ground_truth"] for claim in source_claims):
            raise ValueError(f"Attribute {spec['id']} depends on quarantined claims.")
        authority = min(claim["authority"] for claim in source_claims)
        record = {
            **spec,
            "record_type": "attribute",
            "model_id": "claude-fable-5",
            "subject_model": "claude-fable-5",
            "comparison_models": ["claude-opus-4-8", "claude-mythos-5", "claude-sonnet-5"],
            "source_id": source_claims[0]["source_id"],
            "source_level": source_claims[0]["source_level"],
            "source_urls": sorted({claim["source_url"] for claim in source_claims}),
            "authority": authority,
            "audit_relevance": 1.0,
            "eligible_for_ground_truth": True,
            "fallback_contaminated": False,
            "effective_from": min(
                claim["effective_from"] for claim in source_claims if claim["effective_from"]
            ),
        }
        record["embedding_text"] = (
            f"模型：Claude Fable 5\n"
            f"审计属性：{record['title']}\n"
            f"预期信号：{record['expected_signal']}\n"
            f"对比信号：{record['contrast_signal']}\n"
            f"测量方法：{record['measurement']}\n"
            f"测试配置：{record['test_config']}"
        )
        record["content_hash"] = _sha256(
            json.dumps(record, ensure_ascii=False, sort_keys=True)
        )
        attributes.append(record)
    return attributes


def _download_benchmark_assets(
    assets: list[dict[str, Any]],
    output_root: Path,
) -> list[dict[str, Any]]:
    asset_root = output_root / "assets"
    asset_root.mkdir(parents=True, exist_ok=True)
    seen_urls: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    for asset in assets:
        if asset["role"] != "benchmark_image_pending_verification":
            continue
        if asset["url"] in seen_urls:
            duplicate = {**asset, **seen_urls[asset["url"]], "duplicate_asset": True}
            results.append(duplicate)
            continue
        record = {**asset, "duplicate_asset": False, "ocr_status": "not_run"}
        try:
            response = requests.get(asset["url"], timeout=60)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            extension = ".png" if "png" in content_type else ".img"
            target = asset_root / f"{asset['asset_id']}{extension}"
            target.write_bytes(response.content)
            record.update(
                {
                    "download_status": "success",
                    "local_path": str(target.relative_to(output_root)).replace("\\", "/"),
                    "bytes": len(response.content),
                    "sha256": _sha256(response.content),
                }
            )
        except Exception as exc:
            record.update({"download_status": "failed", "error": str(exc)})
        seen_urls[asset["url"]] = {
            key: value
            for key, value in record.items()
            if key in {"download_status", "local_path", "bytes", "sha256", "ocr_status"}
        }
        results.append(record)
    return results


def process_fable5(
    raw_root: Path,
    output_root: Path,
    *,
    download_assets: bool = True,
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    clean_root = output_root / "clean"
    clean_root.mkdir(parents=True, exist_ok=True)
    source_files = sorted(raw_root.rglob("content.md"))
    if len(source_files) != 5:
        raise ValueError(f"Expected 5 Fable 5 source files, found {len(source_files)}.")

    documents: dict[str, dict[str, Any]] = {}
    all_sections: list[dict[str, Any]] = []
    all_assets: list[dict[str, Any]] = []
    dropped_sections: list[dict[str, Any]] = []
    for source_file in source_files:
        raw_text = source_file.read_text(encoding="utf-8")
        front_matter, clean_text, assets, dropped = _clean_source(
            source_file.parent.name,
            raw_text,
        )
        source_id = front_matter.get("source_id", source_file.parent.name)
        clean_path = clean_root / f"{source_id}.md"
        clean_path.write_text(clean_text, encoding="utf-8")
        document = {
            "source_id": source_id,
            "front_matter": front_matter,
            "clean_text": clean_text,
            "raw_characters": len(raw_text),
            "clean_characters": len(clean_text),
            "clean_sha256": _sha256(clean_text),
            "clean_path": str(clean_path.relative_to(output_root)).replace("\\", "/"),
        }
        documents[source_id] = document
        all_assets.extend(assets)
        dropped_sections.extend(dropped)
        all_sections.extend(
            _sections(
                source_id=source_id,
                source_level=front_matter.get("priority", ""),
                source_url=front_matter.get("source_url", ""),
                clean_text=clean_text,
            )
        )

    claims = _build_claims(documents)
    attributes = _build_attributes(claims)
    benchmark_assets = (
        _download_benchmark_assets(all_assets, output_root) if download_assets else []
    )
    quarantined_claims = [
        claim for claim in claims if not claim["eligible_for_ground_truth"]
    ]
    ground_truth_claims = [
        claim for claim in claims if claim["eligible_for_ground_truth"]
    ]
    duplicate_hashes = {
        digest
        for digest in (record["content_hash"] for record in ground_truth_claims + attributes)
        if sum(
            item["content_hash"] == digest
            for item in ground_truth_claims + attributes
        )
        > 1
    }
    if duplicate_hashes:
        raise ValueError(f"Duplicate ground-truth record hashes: {sorted(duplicate_hashes)}")

    return {
        "documents": [
            {key: value for key, value in document.items() if key != "clean_text"}
            for document in documents.values()
        ],
        "sections": all_sections,
        "claims": claims,
        "ground_truth_claims": ground_truth_claims,
        "attributes": attributes,
        "assets": all_assets,
        "benchmark_assets": benchmark_assets,
        "quarantine": {
            "claims": quarantined_claims,
            "benchmark_assets": benchmark_assets,
            "dropped_sections": dropped_sections,
        },
        "stats": {
            "documents": len(documents),
            "sections": len(all_sections),
            "claims": len(claims),
            "ground_truth_claims": len(ground_truth_claims),
            "quarantined_claims": len(quarantined_claims),
            "attributes": len(attributes),
            "images_found": len(all_assets),
            "benchmark_images": len(benchmark_assets),
            "records_for_embedding": len(ground_truth_claims) + len(attributes),
        },
    }
