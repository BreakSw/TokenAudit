import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus from "element-plus"
import { createMemoryHistory, createRouter } from "vue-router"
import { describe, expect, it, vi } from "vitest"

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
      stubs: {
        ElCheckbox: { template: "<span />" },
        ElCheckboxGroup: { template: "<div><slot /></div>" }
      }
    }
  })
}

function buttonWithText(wrapper, text) {
  const button = wrapper.findAll("button").find((candidate) => candidate.text().trim() === text)
  expect(button, `button ${text}`).toBeTruthy()
  return button
}

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
    vi.mocked(listTokens).mockResolvedValue([{ id: 7, name: "primary", tokenMasked: "tok-***" }])
    vi.mocked(startAudit).mockResolvedValue({ auditId: 42 })
    vi.mocked(getAudit)
      .mockResolvedValueOnce({ status: "running", progress: 30 })
      .mockResolvedValueOnce({ status: "completed", progress: 95 })
    vi.mocked(listAuditEvents).mockResolvedValue([])

    const wrapper = await mountAuditForm()
    await flushPromises()
    expect(wrapper.get(".audit-card").exists()).toBe(true)

    await buttonWithText(wrapper, "开始审计").trigger("click")
    await flushPromises()
    expect(wrapper.text()).toContain("审计ID：42")
    expect(wrapper.text()).toContain("30%")

    await buttonWithText(wrapper, "刷新").trigger("click")
    await flushPromises()
    expect(wrapper.text()).toContain("100%")
    expect(wrapper.text()).toContain("已完成")
  })
})
