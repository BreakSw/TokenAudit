import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus, { ElMessage } from "element-plus"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import ReportView from "./ReportView.vue"
import { getAudit, listAuditEvents } from "../request/api"

vi.mock("../request/api", () => ({
  getAudit: vi.fn(),
  listAuditEvents: vi.fn()
}))

function deferred() {
  let resolve
  let reject
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

function completedReport(overrides = {}) {
  return {
    id: 42,
    status: "completed",
    progress: 100,
    auditTime: "2026-08-08 10:20:30",
    overallConclusion: "综合风险可控",
    report: {
      base_info: {
        token_masked: "sk-***-safe",
        platform: "OpenAI Compatible",
        claimed_model: "gpt-audit-1",
        audit_time: "2026-08-08 10:20:30"
      },
      overall: {
        overall_conclusion: "综合风险可控",
        risk_warnings: ["限制匿名访问", "复核模型路由"],
        usage_suggestions: ["轮换高风险 Token", "启用调用限流"]
      },
      sections: {
        security: { conclusion: "安全性待加固", evidence: "匿名调用返回 401" },
        stability: { conclusion: "响应稳定", evidence: "三次调用差异较小" },
        compliance: { conclusion: "合规", evidence: "未发现敏感信息泄露" },
        watering: { conclusion: "未见明显掺水", evidence: "能力特征一致" },
        permission: { conclusion: "权限边界正常", evidence: "非宣称模型被拒绝" },
        validity: { conclusion: "有效", evidence: "连续调用成功" }
      },
      report_markdown: "# 审计报告\n<script>alert('xss')</script>",
      ...overrides
    }
  }
}

async function mountReport(auditId = 42) {
  return mount(ReportView, {
    attachTo: document.body,
    props: { auditId },
    global: {
      plugins: [ElementPlus],
      directives: { reveal: () => {} },
      mocks: { $router: { push: vi.fn() } }
    }
  })
}

beforeEach(() => {
  vi.mocked(getAudit).mockResolvedValue(completedReport())
  vi.mocked(listAuditEvents).mockResolvedValue([
    { id: 1, ts: "2026-08-08T10:20:30.000Z", event: "audit_completed", payload: { overallConclusion: "通过" } }
  ])
})

afterEach(() => {
  vi.clearAllMocks()
})

describe("ReportView content", () => {
  it("renders the summary, advice and six dimensions in canonical order", async () => {
    const wrapper = await mountReport()
    await flushPromises()

    expect(wrapper.get("[data-testid='report-title']").text()).toContain("#42")
    expect(wrapper.get("[data-testid='overall-conclusion']").text()).toContain("综合风险可控")
    expect(wrapper.get("[data-testid='risk-list']").text()).toContain("限制匿名访问")
    expect(wrapper.get("[data-testid='suggestion-list']").text()).toContain("启用调用限流")

    const dimensions = wrapper.findAll("[data-testid='report-dimension']")
    expect(dimensions.map((item) => item.attributes("data-dimension"))).toEqual([
      "validity",
      "permission",
      "watering",
      "compliance",
      "stability",
      "security"
    ])
    expect(dimensions.map((item) => item.find("h3").text())).toEqual([
      "有效性",
      "权限",
      "模型真实性",
      "合规",
      "稳定性",
      "安全性"
    ])
    expect(wrapper.text()).toContain("六个维度")
    expect(wrapper.text()).not.toContain("5项")
  })

  it("shows Markdown as inert text and never injects report HTML", async () => {
    const wrapper = await mountReport()
    await flushPromises()

    expect(wrapper.get("[data-testid='markdown-output']").text()).toContain("<script>alert('xss')</script>")
    expect(wrapper.find("[data-testid='markdown-output'] script").exists()).toBe(false)
  })

  it("renders deep audit score cards instead of empty quick-audit dimensions", async () => {
    vi.mocked(getAudit).mockResolvedValue(completedReport({
      base_info: {
        audit_mode: "deep",
        token_masked: "sk-***-safe",
        platform: "relay",
        claimed_model: "model-x",
        audit_time: "2026-08-25 10:20:30"
      },
      deep_audit: { questions_per_round: 3, variants_per_question: 3 },
      ground_truth: { evidence_counts: { spec: 5, claimed_behavior: 8, contrast_behavior: 8 } },
      rounds: [{ responses: [{ ok: true }, { ok: false }, { ok: true }] }],
      score: {
        total_score: 82.4,
        band: "consistent",
        confidence: 0.76,
        valid_response_ratio: 0.6667,
        components: {
          objective: 81,
          semantic: 79,
          official_ground_truth: 77,
          behavior_differential: 72,
          fuzz_consistency: 90
        }
      }
    }))

    const wrapper = await mountReport()
    await flushPromises()

    expect(wrapper.text()).toContain("五项深度评分")
    expect(wrapper.text()).toContain("RAG 证据、动态探针、模糊变体与多 Agent 裁判")
    const dimensions = wrapper.findAll("[data-testid='report-dimension']")
    expect(dimensions.map((item) => item.attributes("data-dimension"))).toEqual([
      "objective",
      "semantic",
      "official_ground_truth",
      "behavior_differential",
      "fuzz_consistency"
    ])
    expect(dimensions.map((item) => item.find("h3").text())).toEqual([
      "客观约束",
      "语义质量",
      "基线符合度",
      "行为差分",
      "Fuzz 一致性"
    ])
    expect(wrapper.text()).toContain("81.00 / 100")
    expect(wrapper.text()).toContain("3 次目标响应，2 次返回可评分答案")
    expect(wrapper.text()).not.toContain("未返回分项结论")
    const overallScore = wrapper.get("[data-testid='report-overall-score']")
    expect(overallScore.text()).toContain("综合得分")
    expect(overallScore.text()).toContain("82.40")
    expect(overallScore.text()).toContain("一致")
    expect(overallScore.text()).toContain("76.0%")
    expect(overallScore.text()).toContain("66.7%")
  })

  it("defaults an English deep-audit verdict to a Chinese summary", async () => {
    const englishReport = completedReport({
      base_info: { audit_mode: "deep", claimed_model: "model-x" },
      ground_truth: { coverage: 0.15, evidence_counts: {} },
      deep_audit: { questions_per_round: 3, variants_per_question: 3 },
      score: {
        total_score: 72.96,
        band: "partially_consistent",
        confidence: 0.0933,
        valid_response_ratio: 0.8889,
        components: {}
      },
      overall: {
        overall_conclusion: "The result is partially consistent with the declared baseline.",
        risk_warnings: ["Weak knowledge coverage."],
        usage_suggestions: ["Run more tests."]
      }
    })
    englishReport.overallConclusion = "The result is partially consistent with the declared baseline."
    vi.mocked(getAudit).mockResolvedValue(englishReport)

    const wrapper = await mountReport()
    await flushPromises()

    expect(wrapper.get('[data-testid="overall-conclusion"]').text()).toContain("部分一致")
    expect(wrapper.get('[data-testid="overall-conclusion"]').text()).toContain("72.96")
    expect(wrapper.get('[data-testid="risk-list"]').text()).toContain("知识基线覆盖率")
    expect(wrapper.get('[data-testid="risk-list"]').text()).toContain("仅按成功答案评分")
    expect(wrapper.get('[data-testid="suggestion-list"]').text()).toContain("官方模型文档")
  })
  it("does not describe an HTTP 402 target rejection as an invalid answer", async () => {
    vi.mocked(listAuditEvents).mockResolvedValue([
      {
        id: 1,
        ts: "2026-08-25T10:20:30.000Z",
        event: "deep_target_call_end",
        payload: { ok: false, status_code: 402, elapsed_ms: 18, response_chars: 0 }
      }
    ])

    const wrapper = await mountReport()
    await flushPromises()
    await wrapper.findAll('[role="tab"]')[2].trigger("click")

    expect(wrapper.text()).toContain("HTTP 402")
    expect(wrapper.text()).not.toContain("\u7b54\u6848\u65e0\u6548")
  })
})

describe("ReportView polling lifecycle", () => {
  it("coalesces timer refreshes while one request is still pending", async () => {
    vi.useFakeTimers()
    const pending = deferred()
    vi.mocked(getAudit).mockResolvedValueOnce({ status: "running", progress: 12 }).mockReturnValue(pending.promise)

    await mountReport()
    await flushPromises()
    await vi.advanceTimersByTimeAsync(3200)

    expect(getAudit).toHaveBeenCalledTimes(2)
    pending.resolve({ status: "running", progress: 30 })
    await flushPromises()
  })

  it("does not apply an old audit response after the audit id changes", async () => {
    const oldResponse = deferred()
    vi.mocked(getAudit).mockImplementation((id) => {
      if (id === 42) return oldResponse.promise
      const latest = completedReport({
        overall: { overall_conclusion: "新报告结论", risk_warnings: [], usage_suggestions: [] }
      })
      latest.overallConclusion = "新报告结论"
      return Promise.resolve(latest)
    })
    vi.mocked(listAuditEvents).mockResolvedValue([])

    const wrapper = await mountReport(42)
    await wrapper.setProps({ auditId: 99 })
    await flushPromises()

    expect(wrapper.text()).toContain("新报告结论")
    const stale = completedReport({
      overall: { overall_conclusion: "旧报告结论", risk_warnings: [], usage_suggestions: [] }
    })
    stale.overallConclusion = "旧报告结论"
    oldResponse.resolve(stale)
    await flushPromises()

    expect(wrapper.text()).toContain("新报告结论")
    expect(wrapper.text()).not.toContain("旧报告结论")
  })

  it("does not continue a pending request after unmount", async () => {
    const pending = deferred()
    vi.mocked(getAudit).mockReturnValue(pending.promise)
    const messageSpy = vi.spyOn(ElMessage, "error")

    const wrapper = await mountReport()
    wrapper.unmount()
    pending.reject(new Error("late failure"))
    await flushPromises()

    expect(listAuditEvents).not.toHaveBeenCalled()
    expect(messageSpy).not.toHaveBeenCalled()
  })
})
