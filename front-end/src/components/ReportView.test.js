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
