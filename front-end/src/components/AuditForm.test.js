import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus, { ElMessage, ElMessageBox } from "element-plus"
import { createMemoryHistory, createRouter } from "vue-router"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import AuditForm from "./AuditForm.vue"
import { cancelAudit, getAudit, getAuditAiConfig, listAuditEvents, listAudits, listTokens, startAudit } from "../request/api"

const wrappers = []

function deferred() {
  let resolve
  let reject
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

vi.mock("../request/api", () => ({
  cancelAudit: vi.fn(),
  getAudit: vi.fn(),
  getAuditAiConfig: vi.fn(),
  listAuditEvents: vi.fn(),
  listAudits: vi.fn(),
  listTokens: vi.fn(),
  startAudit: vi.fn()
}))

async function mountAuditForm(provide = {}) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/audit", component: AuditForm },
      { path: "/tokens", component: { template: "<div />" } },
      { path: "/history", component: { template: "<div />" } },
      { path: "/report/:id", component: { template: "<div />" } }
    ]
  })
  await router.push("/audit")
  await router.isReady()
  const wrapper = mount(AuditForm, {
    attachTo: document.body,
    global: {
      plugins: [router, ElementPlus],
      provide,
      directives: {
        reveal: () => {}
      }
    }
  })
  wrappers.push(wrapper)
  return wrapper
}

function buttonWithText(wrapper, text) {
  const button = wrapper.findAll("button").find((candidate) => candidate.text().trim() === text)
  expect(button, `button ${text}`).toBeTruthy()
  return button
}

beforeEach(() => {
  localStorage.clear()
  vi.mocked(listTokens).mockResolvedValue([{ id: 7, name: "主审计 Token", tokenMasked: "tok-***" }])
  vi.mocked(getAuditAiConfig).mockResolvedValue({ configured: true })
  vi.mocked(getAudit).mockResolvedValue({ status: "running", progress: 42 })
  vi.mocked(listAuditEvents).mockResolvedValue([])
  vi.mocked(listAudits).mockResolvedValue([])
  vi.mocked(cancelAudit).mockResolvedValue({ id: 42, status: "cancelled", progress: 100 })
})

afterEach(() => {
  wrappers.splice(0).forEach((wrapper) => wrapper.unmount())
  vi.clearAllTimers()
  vi.useRealTimers()
  document.body.innerHTML = ""
  vi.restoreAllMocks()
  vi.clearAllMocks()
})

describe("AuditForm polling lifecycle", () => {
  it("opens audit AI settings and blocks submission when the configuration is missing", async () => {
    const openAuditAiSettings = vi.fn()
    vi.mocked(getAuditAiConfig).mockResolvedValue({ configured: false })
    const wrapper = await mountAuditForm({ openAuditAiSettings })
    await flushPromises()

    await wrapper.get(".configuration-actions button").trigger("click")
    await flushPromises()

    expect(startAudit).not.toHaveBeenCalled()
    expect(openAuditAiSettings).toHaveBeenCalledWith(expect.stringContaining("请配置审计 API Key"))
  })

  it("coalesces consecutive refreshes for the same audit", async () => {
    vi.useFakeTimers()
    const auditResponse = deferred()
    vi.mocked(getAudit).mockReturnValue(auditResponse.promise)
    vi.mocked(startAudit).mockResolvedValue({ auditId: 42 })

    const wrapper = await mountAuditForm()
    await flushPromises()
    await wrapper.get(".configuration-actions button").trigger("click")
    await flushPromises()
    await vi.advanceTimersByTimeAsync(2400)

    expect(getAudit).toHaveBeenCalledTimes(1)
    expect(getAudit).toHaveBeenCalledWith(42)

    auditResponse.resolve({ status: "running", progress: 12 })
    await flushPromises()
    expect(listAuditEvents).toHaveBeenCalledTimes(1)
    expect(listAuditEvents).toHaveBeenCalledWith(42)
  })

  it("keeps an old audit response from overwriting or stopping a newly submitted audit", async () => {
    vi.useFakeTimers()
    localStorage.setItem("lastAuditId", "42")
    const oldAuditResponse = deferred()
    vi.mocked(getAudit).mockImplementation((id) => {
      if (id === 42) return oldAuditResponse.promise
      return Promise.resolve({ status: "running", progress: 17 })
    })
    vi.mocked(listAuditEvents).mockImplementation((id) =>
      Promise.resolve([{ ts: `2026-08-08T08:16:3${id === 42 ? 2 : 9}.123Z`, event: "audit_start", payload: { auditId: id } }])
    )
    vi.mocked(startAudit).mockResolvedValue({ auditId: 99 })

    const wrapper = await mountAuditForm()
    await flushPromises()
    await wrapper.get(".configuration-actions button").trigger("click")
    await flushPromises()

    expect(getAudit).toHaveBeenCalledWith(42)
    expect(getAudit).toHaveBeenCalledWith(99)
    expect(listAuditEvents).toHaveBeenCalledWith(99)
    expect(wrapper.text()).toContain("17%")

    oldAuditResponse.resolve({ status: "completed", progress: 95 })
    await flushPromises()

    expect(listAuditEvents).toHaveBeenCalledWith(42)
    expect(wrapper.text()).toContain("17%")
    expect(wrapper.text()).toContain("99")
    expect(localStorage.getItem("lastAuditId")).toBe("99")

    const callsBeforeNextPoll = vi.mocked(getAudit).mock.calls.filter(([id]) => id === 99).length
    await vi.advanceTimersByTimeAsync(1200)
    await flushPromises()
    expect(vi.mocked(getAudit).mock.calls.filter(([id]) => id === 99)).toHaveLength(callsBeforeNextPoll + 1)
  })

  it("does not continue a pending refresh after unmount", async () => {
    localStorage.setItem("lastAuditId", "42")
    const auditResponse = deferred()
    vi.mocked(getAudit).mockReturnValue(auditResponse.promise)

    const wrapper = await mountAuditForm()
    await flushPromises()
    wrapper.unmount()
    auditResponse.resolve({ status: "running", progress: 80 })
    await flushPromises()

    expect(listAuditEvents).not.toHaveBeenCalled()
  })
})

describe("AuditForm stage state derivation", () => {
  it("maps a composite phase start to both active stages and an accurate current label", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(listAuditEvents).mockResolvedValue([
      {
        id: 1,
        ts: "2026-08-08T08:15:00.000Z",
        event: "phase_start",
        payload: { phase: "compliance_stability" }
      }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()
    const stages = wrapper.findAll('[data-testid="audit-stage"]')

    expect(stages[3].classes()).toContain("audit-stage--running")
    expect(stages[4].classes()).toContain("audit-stage--running")
    expect(wrapper.get(".progress-copy span").text()).toBe("合规审计 / 稳定性审计")
  })

  it("maps a successful composite phase end to both completed stages", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(listAuditEvents).mockResolvedValue([
      { id: 1, event: "phase_start", payload: { phase: "compliance_stability" } },
      { id: 2, event: "phase_end", payload: { phase: "compliance_stability", status: "success" } }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()
    const stages = wrapper.findAll('[data-testid="audit-stage"]')

    expect(stages[3].classes()).toContain("audit-stage--completed")
    expect(stages[4].classes()).toContain("audit-stage--completed")
  })

  it("preserves both composite phase failures when the overall audit completes", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(getAudit).mockResolvedValue({ status: "completed", progress: 100 })
    vi.mocked(listAuditEvents).mockResolvedValue([
      { id: 1, event: "phase_start", payload: { phase: "compliance_stability" } },
      { id: 2, event: "phase_end", payload: { phase: "compliance_stability", status: "error" } },
      { id: 3, event: "audit_completed", payload: {} }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()
    const stages = wrapper.findAll('[data-testid="audit-stage"]')

    expect(stages[3].classes()).toContain("audit-stage--failed")
    expect(stages[4].classes()).toContain("audit-stage--failed")
    expect(stages[2].classes()).toContain("audit-stage--pending")
  })

  it("preserves failed and pending stages when the overall audit completes", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(getAudit).mockResolvedValue({ status: "completed", progress: 100 })
    vi.mocked(listAuditEvents).mockResolvedValue([
      { id: 1, ts: "2026-08-08T08:16:20.000Z", event: "phase_start", payload: { phase: "validity" } },
      {
        id: 2,
        ts: "2026-08-08T08:16:21.000Z",
        event: "phase_end",
        payload: { phase: "validity", status: "error" }
      },
      { id: 3, ts: "2026-08-08T08:16:22.000Z", event: "phase_start", payload: { phase: "permission" } },
      {
        id: 4,
        ts: "2026-08-08T08:16:23.000Z",
        event: "phase_end",
        payload: { phase: "permission", status: "success" }
      },
      {
        id: 5,
        ts: "2026-08-08T08:16:24.000Z",
        event: "deepseek_call_start",
        payload: { phase: "overall", model: "deepseek-chat" }
      },
      {
        id: 6,
        ts: "2026-08-08T08:16:25.000Z",
        event: "deepseek_call_end",
        payload: { phase: "overall", elapsed_ms: 900 }
      },
      { id: 7, ts: "2026-08-08T08:16:26.000Z", event: "audit_completed", payload: {} }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()
    const stages = wrapper.findAll('[data-testid="audit-stage"]')

    expect(stages[0].classes()).toContain("audit-stage--failed")
    expect(stages[0].text()).toContain("中断")
    expect(stages[1].classes()).toContain("audit-stage--completed")
    expect(stages[2].classes()).toContain("audit-stage--pending")
    expect(stages[6].classes()).toContain("audit-stage--completed")
  })

  it("marks an ended phase completed and leaves no stage running when a later audit failure has no active phase", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(getAudit).mockResolvedValue({ status: "failed", progress: 54 })
    vi.mocked(listAuditEvents).mockResolvedValue([
      { ts: "2026-08-08T08:16:30.000Z", event: "phase_start", payload: { phase: "security" } },
      {
        ts: "2026-08-08T08:16:31.000Z",
        event: "token_call_start",
        payload: { model: "gpt-security-1", scenario: "prompt-injection" }
      },
      {
        ts: "2026-08-08T08:16:32.000Z",
        event: "token_call_end",
        payload: { status_code: 200, elapsed_ms: 684 }
      },
      {
        ts: "2026-08-08T08:16:33.000Z",
        event: "phase_end",
        payload: { phase: "security" }
      },
      { ts: "2026-08-08T08:16:34.000Z", event: "audit_failed", payload: { error: "report failed" } }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()
    const stages = wrapper.findAll('[data-testid="audit-stage"]')

    expect(stages[5].classes()).toContain("audit-stage--completed")
    expect(wrapper.findAll(".audit-stage--running")).toHaveLength(0)
    expect(wrapper.findAll(".audit-stage--failed")).toHaveLength(0)
    expect(wrapper.get('[data-testid="audit-failure-detail"]').text()).toContain("report failed")
  })

  it("marks the overall stage completed after a DeepSeek start/end pair", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(listAuditEvents).mockResolvedValue([
      {
        ts: "2026-08-08T08:16:35.000Z",
        event: "deepseek_call_start",
        payload: { phase: "overall", model: "deepseek-chat" }
      },
      {
        ts: "2026-08-08T08:16:36.000Z",
        event: "deepseek_call_end",
        payload: { phase: "overall", status_code: 200, elapsed_ms: 912 }
      }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()
    const stages = wrapper.findAll('[data-testid="audit-stage"]')

    expect(stages[6].classes()).toContain("audit-stage--completed")
    expect(wrapper.findAll(".audit-stage--running")).toHaveLength(0)
  })
})

describe("AuditForm terminal display clearing", () => {
  it("clears only the terminal while preserving stage truth and uses a value fallback for events without ids", async () => {
    localStorage.setItem("lastAuditId", "42")
    const initialEvents = [
      { ts: "2026-08-08T08:17:00.000Z", event: "phase_start", payload: { phase: "validity" } },
      {
        ts: "2026-08-08T08:17:01.000Z",
        event: "phase_end",
        payload: { phase: "validity", status: "error" }
      },
      { ts: "2026-08-08T08:17:02.000Z", event: "audit_start", payload: {} }
    ]
    const newEvent = { ts: "2026-08-08T08:17:03.000Z", event: "audit_failed", payload: { error: "late event" } }
    vi.mocked(listAuditEvents)
      .mockResolvedValueOnce(initialEvents)
      .mockResolvedValueOnce([...initialEvents, newEvent])

    const wrapper = await mountAuditForm()
    await flushPromises()
    expect(wrapper.findAll('[data-testid="terminal-event"]')).toHaveLength(3)

    await buttonWithText(wrapper, "清空显示").trigger("click")
    expect(wrapper.findAll('[data-testid="terminal-event"]')).toHaveLength(0)
    expect(wrapper.findAll('[data-testid="audit-stage"]')[0].classes()).toContain("audit-stage--failed")

    await buttonWithText(wrapper, "刷新进度").trigger("click")
    await flushPromises()
    const visibleRows = wrapper.findAll('[data-testid="terminal-event"]')
    expect(visibleRows).toHaveLength(1)
    expect(visibleRows[0].get('[data-testid="event-tag"]').text()).toBe("audit_failed")
    expect(wrapper.findAll('[data-testid="audit-stage"]')[0].classes()).toContain("audit-stage--failed")
  })

  it("uses increasing event ids as the clear boundary", async () => {
    localStorage.setItem("lastAuditId", "42")
    const oldEvent = { id: 100, ts: "2026-08-08T08:18:00.000Z", event: "audit_start", payload: {} }
    const newEvent = { id: 101, ts: "2026-08-08T08:18:01.000Z", event: "audit_failed", payload: {} }
    vi.mocked(listAuditEvents).mockResolvedValueOnce([oldEvent]).mockResolvedValueOnce([oldEvent, newEvent])

    const wrapper = await mountAuditForm()
    await flushPromises()
    await buttonWithText(wrapper, "清空显示").trigger("click")
    await buttonWithText(wrapper, "刷新进度").trigger("click")
    await flushPromises()

    const visibleRows = wrapper.findAll('[data-testid="terminal-event"]')
    expect(visibleRows).toHaveLength(1)
    expect(visibleRows[0].get('[data-testid="event-tag"]').text()).toBe("audit_failed")
  })

  it("resets the clear boundary when a new audit is submitted", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(getAudit)
      .mockResolvedValueOnce({ status: "completed", progress: 100 })
      .mockResolvedValueOnce({ status: "running", progress: 5 })
    vi.mocked(listAuditEvents)
      .mockResolvedValueOnce([{ id: 100, ts: "2026-08-08T08:19:00.000Z", event: "audit_completed", payload: {} }])
      .mockResolvedValueOnce([{ id: 1, ts: "2026-08-08T08:19:01.000Z", event: "audit_start", payload: {} }])
    vi.mocked(startAudit).mockResolvedValue({ auditId: 99 })

    const wrapper = await mountAuditForm()
    await flushPromises()
    await buttonWithText(wrapper, "清空显示").trigger("click")
    await buttonWithText(wrapper, "开始审计").trigger("click")
    await flushPromises()

    const visibleRows = wrapper.findAll('[data-testid="terminal-event"]')
    expect(visibleRows).toHaveLength(1)
    expect(visibleRows[0].get('[data-testid="event-tag"]').text()).toBe("audit_start")
    expect(wrapper.text()).toContain("99")
  })
})

describe("AuditForm token loading states", () => {
  it("distinguishes loading from a genuinely empty token list", async () => {
    const tokensResponse = deferred()
    vi.mocked(listTokens).mockReturnValue(tokensResponse.promise)

    const wrapper = await mountAuditForm()
    await flushPromises()
    expect(wrapper.get('.token-field [role="status"]').text()).toContain("正在加载")

    tokensResponse.resolve([])
    await flushPromises()
    expect(wrapper.get('.token-field [role="status"]').text()).toContain("暂无可用 Token")
    expect(wrapper.text()).not.toContain("正在加载")
  })

  it("keeps a token error visible and retries successfully", async () => {
    const tokensResponse = deferred()
    vi.mocked(listTokens).mockReturnValueOnce(tokensResponse.promise).mockResolvedValueOnce([
      { id: 8, name: "Recovery Token", tokenMasked: "tok-***" }
    ])

    const wrapper = await mountAuditForm()
    tokensResponse.reject(new Error("token service unavailable"))
    await flushPromises()

    expect(wrapper.get('.token-field [role="alert"]').text()).toContain("token service unavailable")
    await wrapper.get('[data-testid="retry-tokens"]').trigger("click")
    await flushPromises()
    expect(listTokens).toHaveBeenCalledTimes(2)
    expect(wrapper.text()).toContain("Recovery Token")
    expect(wrapper.find('.token-field [role="alert"]').exists()).toBe(false)
  })

  it("selects the first available token when a reload removes the current selection", async () => {
    vi.mocked(listTokens)
      .mockResolvedValueOnce([{ id: 7, name: "Old Token", tokenMasked: "old-***" }])
      .mockResolvedValueOnce([{ id: 8, name: "New Token", tokenMasked: "new-***" }])
    vi.mocked(startAudit).mockResolvedValue({ auditId: 42 })

    const wrapper = await mountAuditForm()
    await flushPromises()
    await buttonWithText(wrapper, "刷新 Token").trigger("click")
    await flushPromises()
    await buttonWithText(wrapper, "开始审计").trigger("click")
    await flushPromises()

    expect(startAudit).toHaveBeenCalledWith(expect.objectContaining({ tokenId: 8 }))
  })

  it("clears a stale token selection when a reload becomes empty", async () => {
    vi.mocked(listTokens)
      .mockResolvedValueOnce([{ id: 7, name: "Old Token", tokenMasked: "old-***" }])
      .mockResolvedValueOnce([])

    const wrapper = await mountAuditForm()
    await flushPromises()
    await buttonWithText(wrapper, "刷新 Token").trigger("click")
    await flushPromises()
    await buttonWithText(wrapper, "开始审计").trigger("click")
    await flushPromises()

    expect(startAudit).not.toHaveBeenCalled()
  })
})

describe("AuditForm submit lifecycle", () => {
  it("allows multiple audits to be started while another task is running", async () => {
    vi.mocked(startAudit)
      .mockResolvedValueOnce({ auditId: 42 })
      .mockResolvedValueOnce({ auditId: 43 })

    const wrapper = await mountAuditForm()
    await flushPromises()
    await buttonWithText(wrapper, "开始审计").trigger("click")
    await flushPromises()
    await buttonWithText(wrapper, "并行新建审计").trigger("click")
    await flushPromises()

    expect(startAudit).toHaveBeenCalledTimes(2)
    expect(wrapper.findAll('[data-testid="parallel-task"]')).toHaveLength(2)
    expect(wrapper.text()).toContain("43")
  })

  it("terminates the selected audit and renders the cancelled state", async () => {
    vi.mocked(startAudit).mockResolvedValue({ auditId: 42 })
    vi.mocked(getAudit)
      .mockResolvedValueOnce({ status: "running", progress: 30 })
      .mockResolvedValueOnce({ status: "cancelled", progress: 100 })
    vi.mocked(listAuditEvents)
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ id: 9, event: "audit_cancelled", payload: { message: "用户已终止审计" } }])
    vi.spyOn(ElMessageBox, "confirm").mockResolvedValue("confirm")

    const wrapper = await mountAuditForm()
    await flushPromises()
    await buttonWithText(wrapper, "开始审计").trigger("click")
    await flushPromises()
    await buttonWithText(wrapper, "终止审计").trigger("click")
    await flushPromises()

    expect(cancelAudit).toHaveBeenCalledWith(42)
    expect(wrapper.text()).toContain("已终止")
    expect(wrapper.text()).toContain("用户已终止审计")
    expect(wrapper.find('[data-testid="cancel-current-audit"]').exists()).toBe(false)
  })

  it("does not toast when a pending submit rejects after unmount", async () => {
    const submitResponse = deferred()
    const errorToast = vi.spyOn(ElMessage, "error")
    vi.mocked(startAudit).mockReturnValue(submitResponse.promise)

    const wrapper = await mountAuditForm()
    await flushPromises()
    await buttonWithText(wrapper, "开始审计").trigger("click")
    wrapper.unmount()
    submitResponse.reject(new Error("late submit failure"))
    await flushPromises()

    expect(errorToast).not.toHaveBeenCalled()
  })
})

describe("AuditForm presentation", () => {
  it("renders the four-part live audit console and all seven stages", async () => {
    const wrapper = await mountAuditForm()
    await flushPromises()

    expect(wrapper.findAll('[data-testid="audit-major-section"]')).toHaveLength(4)
    expect(wrapper.get('[data-testid="audit-heading"]').text()).toContain("实时审计工作流")
    expect(wrapper.get('[data-testid="audit-configuration"]').text()).toContain("Token 与导出配置")
    expect(wrapper.get('[data-testid="audit-pipeline"]').text()).toContain("七阶段审计管线")
    expect(wrapper.get('[data-testid="audit-terminal"]').text()).toContain("实时事件终端")

    const stages = wrapper.findAll('[data-testid="audit-stage"]')
    expect(stages).toHaveLength(7)
    expect(stages.map((stage) => stage.text())).toEqual(
      expect.arrayContaining([
        expect.stringContaining("有效性"),
        expect.stringContaining("权限"),
        expect.stringContaining("模型真实性"),
        expect.stringContaining("合规"),
        expect.stringContaining("稳定性"),
        expect.stringContaining("安全性"),
        expect.stringContaining("综合判定")
      ])
    )
    expect(wrapper.text()).toContain("六个审计维度 + 综合判定")
    expect(wrapper.text()).not.toContain("新手教程")
  })

  it("renders schema-accurate event details, list semantics, parseable time, and falsy payload values", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(listAuditEvents).mockResolvedValue([
      {
        ts: "2026-08-08T08:16:30.123Z",
        event: "phase_start",
        payload: { phase: "security" }
      },
      {
        ts: "2026-08-08T08:16:31.123Z",
        event: "token_call_start",
        payload: { model: "gpt-security-1", scenario: "prompt-injection" }
      },
      {
        ts: "2026-08-08T08:16:32.123Z",
        event: "token_call_end",
        payload: {
          status_code: 0,
          elapsed_ms: 684,
          status: false
        }
      }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()

    expect(getAudit).toHaveBeenCalledWith(42)
    expect(listAuditEvents).toHaveBeenCalledWith(42)
    expect(wrapper.get(".terminal-window").element.tagName).toBe("OL")
    const rows = wrapper.findAll('[data-testid="terminal-event"]')
    expect(rows.every((row) => row.element.tagName === "LI")).toBe(true)
    const startRow = rows.find((row) => row.get('[data-testid="event-tag"]').text() === "token_call_start")
    const endRow = rows.find((row) => row.get('[data-testid="event-tag"]').text() === "token_call_end")
    const timestamp = endRow.get('[data-testid="event-timestamp"]')
    expect(timestamp.text()).toContain("2026-08-08")
    expect(Number.isNaN(Date.parse(timestamp.attributes("datetime")))).toBe(false)
    expect(endRow.get('[data-testid="event-explanation"]').text()).toContain("中转返回")
    expect(endRow.text()).toContain("网络错误")
    expect(endRow.text()).not.toContain("HTTP 0")
    expect(endRow.text()).toContain("684 ms")
    expect(endRow.text()).toContain("RESULT")
    expect(endRow.text()).toContain("false")
    expect(startRow.text()).toContain("gpt-security-1")
    expect(startRow.text()).toContain("prompt-injection")
    expect(rows[0].text()).toContain("安全性")
  })
})

describe("AuditForm storage resilience", () => {
  it("mounts, submits, and refreshes when last-audit storage is blocked", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError")
    })
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError")
    })
    vi.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError")
    })
    vi.mocked(startAudit).mockResolvedValue({ auditId: 42 })
    vi.mocked(getAudit)
      .mockResolvedValueOnce({ status: "running", progress: 30 })
      .mockResolvedValueOnce({ status: "completed", progress: 95 })

    const wrapper = await mountAuditForm()
    await flushPromises()

    await buttonWithText(wrapper, "开始审计").trigger("click")
    await flushPromises()
    expect(wrapper.text()).toContain("审计 ID")
    expect(wrapper.text()).toContain("42")
    expect(wrapper.text()).toContain("30%")

    await buttonWithText(wrapper, "刷新进度").trigger("click")
    await flushPromises()
    expect(wrapper.text()).toContain("100%")
    expect(wrapper.text()).toContain("已完成")
  })
})
