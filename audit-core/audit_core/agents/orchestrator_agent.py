from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from audit_core.agents.compliance_stability_agent import ComplianceStabilityAgent, ComplianceStabilityInput
from audit_core.agents.permission_agent import PermissionAgent, PermissionInput
from audit_core.agents.validity_agent import ValidityAgent, ValidityInput
from audit_core.agents.watering_agent import WateringAgent, WateringInput
from audit_core.config import AuditConfig
from audit_core.scripts import deepseek_chat
from audit_core.utils import coerce_json_object, log_event


@dataclass(frozen=True)
class OrchestratorInput:
    audited_token: str
    platform: str
    token_base_url: str
    claimed_model: str
    non_claimed_model: str
    audit_time: str
    front_end_url: str | None = None
    back_end_url: str | None = None


class OrchestratorAgent:
    name = "调度Agent"

    def run(self, *, config: AuditConfig, inp: OrchestratorInput) -> dict[str, Any]:
        log_event("phase_start", {"phase": "orchestrator", "agent": self.name})
        validity = ValidityAgent().run(
            config=config,
            inp=ValidityInput(
                token_base_url=inp.token_base_url,
                audited_token=inp.audited_token,
                claimed_model=inp.claimed_model,
            ),
        )
        permission = PermissionAgent().run(
            config=config,
            inp=PermissionInput(
                token_base_url=inp.token_base_url,
                audited_token=inp.audited_token,
                claimed_model=inp.claimed_model,
                non_claimed_model=inp.non_claimed_model,
            ),
        )
        watering = WateringAgent().run(
            config=config,
            inp=WateringInput(
                token_base_url=inp.token_base_url,
                audited_token=inp.audited_token,
                claimed_model=inp.claimed_model,
            ),
        )
        cs = ComplianceStabilityAgent().run(
            config=config,
            inp=ComplianceStabilityInput(
                token_base_url=inp.token_base_url,
                audited_token=inp.audited_token,
                claimed_model=inp.claimed_model,
            ),
        )

        sections = {
            "validity": validity,
            "permission": permission,
            "watering": watering,
            "compliance": cs["compliance"],
            "stability": cs["stability"],
        }

        overall = self._overall_judge(config=config, inp=inp, sections=sections)
        report_markdown = build_report_markdown(inp=inp, sections=sections, overall=overall, deepseek_key_masked="已配置(脱敏)")

        log_event("phase_end", {"phase": "orchestrator", "agent": self.name})
        return {
            "base_info": {
                "token_masked": _mask_sensitive(inp.audited_token),
                "platform": inp.platform,
                "claimed_model": inp.claimed_model,
                "audit_time": inp.audit_time,
                "front_end_url": inp.front_end_url,
                "back_end_url": inp.back_end_url,
            },
            "sections": {
                "validity": _normalize_section(validity),
                "permission": _normalize_section(permission),
                "watering": _normalize_section(watering),
                "compliance": _normalize_section(cs["compliance"]),
                "stability": _normalize_section(cs["stability"]),
            },
            "overall": overall,
            "report_markdown": report_markdown,
        }

    def _overall_judge(self, *, config: AuditConfig, inp: OrchestratorInput, sections: dict[str, Any]) -> dict[str, Any]:
        judge_prompt = [
            {
                "role": "system",
                "content": "你是Token综合审计判定模型。只输出JSON对象，不要输出多余文本。",
            },
            {
                "role": "user",
                "content": (
                    "基于以下5项审计结果，输出综合结论与风险建议，必须客观、可追溯。"
                    "输出JSON字段：overall_conclusion、risk_warnings、usage_suggestions。\n\n"
                    f"审计基础信息：{inp}\n\n"
                    f"分项结果：{sections}\n"
                ),
            },
        ]
        log_event("deepseek_call_start", {"phase": "overall", "model": config.deepseek_model})
        judge_raw = deepseek_chat(config=config, messages=judge_prompt)
        log_event("deepseek_call_end", {"phase": "overall", "elapsed_ms": judge_raw.get("elapsed_ms")})
        judge_text = _extract_deepseek_content(judge_raw["response"])
        judge_obj = coerce_json_object(judge_text)
        return {
            "deepseek_judgement": judge_obj,
            "overall_conclusion": judge_obj.get("overall_conclusion") or judge_obj.get("综合审计结论") or judge_text,
            "risk_warnings": judge_obj.get("risk_warnings") or judge_obj.get("风险警示") or [],
            "usage_suggestions": judge_obj.get("usage_suggestions") or judge_obj.get("使用建议") or [],
        }


def _normalize_section(section: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent": section.get("agent"),
        "tests": section.get("tests"),
        "deepseek_judgement": section.get("deepseek_judgement"),
        "conclusion": section.get("conclusion"),
        "evidence": section.get("evidence"),
    }


def _extract_deepseek_content(data: Any) -> str:
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            msg = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
        if isinstance(data.get("text"), str):
            return data["text"]
    return str(data)


def _mask_sensitive(value: str, keep_start: int = 4, keep_end: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep_start + keep_end + 3:
        return value[:2] + "***"
    return value[:keep_start] + "***" + value[-keep_end:]


def build_report_markdown(
    *,
    inp: OrchestratorInput,
    sections: dict[str, Any],
    overall: dict[str, Any],
    deepseek_key_masked: str,
) -> str:
    audit_time = inp.audit_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    token_display = _mask_sensitive(inp.audited_token)
    front_url = inp.front_end_url or ""
    back_url = inp.back_end_url or ""

    v = sections["validity"]
    p = sections["permission"]
    w = sections["watering"]
    c = sections["compliance"]
    s = sections["stability"]

    md = f"""# TokenAudit 完整审计报告（含前后端+多Agent架构关联）
## 1. 审计基础信息
- 待审计Token：{token_display}
- 中转平台：{inp.platform}
- 宣称模型：{inp.claimed_model}
- 审计时间：{audit_time}
- 审计执行项：5项全维度审计
- 审计方式：API调用测试+特征比对+多Agent协同+DeepSeek基座判定
- 审计架构技术栈：Vue3+Element-Plus（前端）、SpringBoot（后端）、Python+LangGraph（多Agent）
- DeepSeek API Key：{deepseek_key_masked}（审计基座）
- 前端部署地址：{front_url}
- 后端服务地址：{back_url}

## 2. 分维度审计结果与证据（含Agent执行记录、DeepSeek判定依据）
### 2.1 Token有效性审计
- 执行Agent：{v.get("agent")}
- 调用测试记录（3次）：
  1.  调用指令：{_safe_prompt(v, 0)}，响应状态码：{_safe_field(v, 0, "status_code")}，响应时间：{_safe_field(v, 0, "elapsed_ms")}ms，响应结果：{_safe_field(v, 0, "response_preview")}
  2.  调用指令：{_safe_prompt(v, 1)}，响应状态码：{_safe_field(v, 1, "status_code")}，响应时间：{_safe_field(v, 1, "elapsed_ms")}ms，响应结果：{_safe_field(v, 1, "response_preview")}
  3.  调用指令：{_safe_prompt(v, 2)}，响应状态码：{_safe_field(v, 2, "status_code")}，响应时间：{_safe_field(v, 2, "elapsed_ms")}ms，响应结果：{_safe_field(v, 2, "response_preview")}
- DeepSeek判定结果：{v.get("deepseek_judgement")}
- 审计结论：{v.get("conclusion")}
- 证据说明：{v.get("evidence")}

### 2.2 Token权限审计
- 执行Agent：{p.get("agent")}
- 权限测试记录：
  1.  测试调用宣称模型：{inp.claimed_model}，结果：{_perm_result(p, 0)}
  2.  测试调用非宣称模型：{inp.non_claimed_model}，结果：{_perm_result(p, 1)}
  3.  匿名调用测试：{inp.claimed_model}，结果：{_perm_result(p, 2)}
- DeepSeek判定结果：{p.get("deepseek_judgement")}
- 审计结论：{p.get("conclusion")}
- 证据说明：{p.get("evidence")}

### 2.3 Token掺水关联审计
- 执行Agent：{w.get("agent")}
- 掺水测试记录（结合模型检测结果）：
  1.  模型响应特征比对：{_water_feature_line(w, 0)}
  2.  多轮调用特征稳定性：{_water_feature_line(w, 1)}
  3.  DeepSeek特征比对结果：{w.get("deepseek_judgement")}
- 审计结论：{w.get("conclusion")}
- 证据说明：{w.get("evidence")}

### 2.4 Token使用合规性审计
- 执行Agent：{c.get("agent")}
- 合规性测试记录：
  1.  Token泄露检测：{_compliance_line(c, "token_leak_check")}
  2.  复用性检测：多设备复用需人工验证（本版本记录匿名调用与接口校验情况）
  3.  调用频率检测：{_compliance_line(c, "high_frequency_calls")}
- DeepSeek判定结果：{c.get("deepseek_judgement")}
- 审计结论：{c.get("conclusion")}
- 证据说明：{c.get("evidence")}

### 2.5 Token稳定性审计
- 执行Agent：{s.get("agent")}
- 稳定性测试记录（5次同一指令调用）：
  1.  调用1：响应时间{_stab_time(s, 0)}ms，结果{_stab_ok(s, 0)}，输出一致性{_stab_sim(s)}
  2.  调用2：响应时间{_stab_time(s, 1)}ms，结果{_stab_ok(s, 1)}，输出一致性{_stab_sim(s)}
  3.  调用3：响应时间{_stab_time(s, 2)}ms，结果{_stab_ok(s, 2)}，输出一致性{_stab_sim(s)}
  4.  调用4：响应时间{_stab_time(s, 3)}ms，结果{_stab_ok(s, 3)}，输出一致性{_stab_sim(s)}
  5.  调用5：响应时间{_stab_time(s, 4)}ms，结果{_stab_ok(s, 4)}，输出一致性{_stab_sim(s)}
- DeepSeek判定结果：{s.get("deepseek_judgement")}
- 审计结论：{s.get("conclusion")}
- 证据说明：{s.get("evidence")}

## 3. 架构关联说明（贴合前后端+多Agent实现）
### 3.1 审计流程与架构联动
1.  前端发起审计请求，将待审计参数提交至SpringBoot后端；
2.  后端调度多Agent审计流程；
3.  各审计Agent执行对应审计任务，调用待审计Token API和DeepSeek API；
4.  调度Agent汇总各Agent结果，提交给DeepSeek模型进行综合判定；
5.  后端将审计结果存储至数据库，同时返回给前端，由前端可视化展示并支持导出。

### 3.2 潜在架构优化建议
- 前端：增加Token加密存储、审计进度实时展示功能，优化报告可视化效果；
- 后端：增加接口限流、异常重试机制，优化多Agent调度效率，扩大数据存储容量；
- 多Agent：增加Agent异常处理逻辑，优化DeepSeek API调用容错机制，提升审计效率；
- 安全：对DeepSeek API Key、待审计Token进行加密处理，避免明文泄露。

## 4. 综合审计结论
{overall.get("overall_conclusion")}

## 5. 风险警示与建议（含架构层面+Token使用层面）
### 5.1 风险警示
{overall.get("risk_warnings")}

### 5.2 使用建议
1.  Token使用层面：{_suggest(overall, 0)}
2.  架构层面：{_suggest(overall, 1)}
3.  审计层面：建议定期使用本审计流程（依托DeepSeek基座+多Agent）对Token进行审计，留存审计记录，及时发现异常问题

备注：本审计报告基于本次测试结果、多Agent协同审计及DeepSeek模型判定生成，审计证据可回溯，仅针对该Token当前状态及对应架构联动效果。
"""
    return md


def _safe_prompt(section: dict[str, Any], idx: int) -> str:
    tests = section.get("tests") or []
    if isinstance(tests, list) and len(tests) > idx:
        return str(tests[idx].get("prompt", ""))
    return ""


def _safe_field(section: dict[str, Any], idx: int, key: str) -> str:
    tests = section.get("tests") or []
    if isinstance(tests, list) and len(tests) > idx:
        return str(tests[idx].get(key, ""))
    return ""


def _perm_result(section: dict[str, Any], idx: int) -> str:
    tests = section.get("tests") or []
    if isinstance(tests, list) and len(tests) > idx:
        t = tests[idx]
        return f"status={t.get('status_code')} ok={t.get('ok')} preview={t.get('response_preview')}"
    return ""


def _water_feature_line(section: dict[str, Any], idx: int) -> str:
    tests = section.get("tests") or []
    if isinstance(tests, list) and len(tests) > idx:
        t = tests[idx]
        return f"features={t.get('features')} preview={t.get('response_preview')}"
    return ""


def _compliance_line(section: dict[str, Any], key: str) -> str:
    tests = section.get("tests") or {}
    return str((tests.get(key) if isinstance(tests, dict) else "") or "")


def _stab_time(section: dict[str, Any], idx: int) -> str:
    tests = section.get("tests") or {}
    calls = tests.get("calls") if isinstance(tests, dict) else []
    if isinstance(calls, list) and len(calls) > idx:
        return str(calls[idx].get("elapsed_ms", ""))
    return ""


def _stab_ok(section: dict[str, Any], idx: int) -> str:
    tests = section.get("tests") or {}
    calls = tests.get("calls") if isinstance(tests, dict) else []
    if isinstance(calls, list) and len(calls) > idx:
        return "成功" if calls[idx].get("ok") else "失败"
    return ""


def _stab_sim(section: dict[str, Any]) -> str:
    tests = section.get("tests") or {}
    if isinstance(tests, dict) and "avg_similarity" in tests:
        return str(tests.get("avg_similarity"))
    return ""


def _suggest(overall: dict[str, Any], idx: int) -> str:
    s = overall.get("usage_suggestions")
    if isinstance(s, list) and len(s) > idx:
        return str(s[idx])
    if isinstance(s, str):
        return s
    return ""
