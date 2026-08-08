import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus from "element-plus"
import { createMemoryHistory, createRouter } from "vue-router"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import AuditForm from "./AuditForm.vue"
import { getAudit, listAuditEvents, listTokens, startAudit } from "../request/api"

vi.mock("../request/api", () => ({
  getAudit: vi.fn(),
  listAuditEvents: vi.fn(),
  listTokens: vi.fn(),
  startAudit: vi.fn()
}))

async function mountAuditForm() {
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
  return mount(AuditForm, {
    attachTo: document.body,
    global: {
      plugins: [router, ElementPlus],
      directives: {
        reveal: () => {}
      }
    }
  })
}

function buttonWithText(wrapper, text) {
  const button = wrapper.findAll("button").find((candidate) => candidate.text().trim() === text)
  expect(button, `button ${text}`).toBeTruthy()
  return button
}

beforeEach(() => {
  localStorage.clear()
  vi.mocked(listTokens).mockResolvedValue([{ id: 7, name: "主审计 Token", tokenMasked: "tok-***" }])
  vi.mocked(getAudit).mockResolvedValue({ status: "running", progress: 42 })
  vi.mocked(listAuditEvents).mockResolvedValue([])
})

afterEach(() => {
  document.body.innerHTML = ""
  vi.restoreAllMocks()
  vi.clearAllMocks()
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

  it("shows timestamp, tag, explanation, status, latency, model and phase for terminal events", async () => {
    localStorage.setItem("lastAuditId", "42")
    vi.mocked(listAuditEvents).mockResolvedValue([
      {
        ts: "2026-08-08T08:16:32.123Z",
        event: "token_call_end",
        payload: {
          status_code: 200,
          elapsed_ms: 684,
          model: "gpt-security-1",
          phase: "security"
        }
      }
    ])

    const wrapper = await mountAuditForm()
    await flushPromises()

    expect(getAudit).toHaveBeenCalledWith(42)
    expect(listAuditEvents).toHaveBeenCalledWith(42)
    const row = wrapper.get('[data-testid="terminal-event"]')
    expect(row.get('[data-testid="event-timestamp"]').text()).toContain("2026-08-08")
    expect(row.get('[data-testid="event-tag"]').text()).toBe("token_call_end")
    expect(row.get('[data-testid="event-explanation"]').text()).toContain("中转返回")
    expect(row.text()).toContain("HTTP 200")
    expect(row.text()).toContain("684 ms")
    expect(row.text()).toContain("gpt-security-1")
    expect(row.text()).toContain("安全性")
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
