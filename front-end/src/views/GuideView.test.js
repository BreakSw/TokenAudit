import { mount } from "@vue/test-utils"
import { beforeEach, describe, expect, it, vi } from "vitest"

import GuideView from "./GuideView.vue"
import * as api from "../request/api"

vi.mock("../request/api", () => ({
  createToken: vi.fn(),
  deleteToken: vi.fn(),
  getAudit: vi.fn(),
  listAuditEvents: vi.fn(),
  listAudits: vi.fn(),
  listTokens: vi.fn(),
  startAudit: vi.fn()
}))

function mountGuide() {
  return mount(GuideView, {
    global: {
      directives: { reveal: { mounted() {} } }
    }
  })
}

beforeEach(() => {
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: { writeText: vi.fn().mockResolvedValue(undefined) }
  })
})

describe("GuideView", () => {
  it("filters the documentation navigation without calling a backend", async () => {
    const wrapper = mountGuide()
    const search = wrapper.get('[data-testid="guide-search"]')

    await search.setValue("环境变量")

    const navigation = wrapper.get('[aria-label="文档导航"]')
    expect(navigation.text()).toContain("配置环境变量")
    expect(navigation.text()).not.toContain("常见错误")
    expect(Object.values(api).every((request) => request.mock.calls.length === 0)).toBe(true)
  })

  it("documents real endpoints and all six audit dimensions", () => {
    const text = mountGuide().text()

    expect(text).toContain("GET /api/agents/health")
    expect(text).toContain("POST /api/audits")
    expect(text).toContain("GET /api/audits/{id}")
    expect(text).toContain("GET /api/audits/{id}/events")
    for (const dimension of ["有效性", "权限", "模型真实性", "合规", "稳定性", "安全性"]) {
      expect(text).toContain(dimension)
    }
  })

  it("separates backend and Vite env files and states the API key rule", () => {
    const wrapper = mountGuide()

    expect(wrapper.text()).toContain("front-end/.env.development")
    expect(wrapper.get('[data-testid="copy-environment"]').text()).not.toContain(
      "VITE_BACKEND_BASE_URL"
    )
    expect(wrapper.get('[data-testid="copy-frontend-environment"]').text()).toContain(
      "VITE_BACKEND_BASE_URL=http://localhost:8086"
    )

    const rule = wrapper.get('[data-testid="api-key-rule"]').text()
    expect(rule).toContain("未启用时可省略")
    expect(rule).toContain("启用后每个 API 请求必须携带")

    for (const sample of ["health", "token", "audit", "events", "report"]) {
      const code = wrapper.get(`[data-testid="copy-${sample}"]`).text()
      expect(code).toContain("curl")
      expect(code).toContain("X-API-KEY")
    }
  })

  it("copies code and reports success accessibly", async () => {
    const wrapper = mountGuide()

    await wrapper.get('[data-testid="copy-health"] button').trigger("click")
    await Promise.resolve()

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      expect.stringContaining("GET /api/agents/health")
    )
    expect(wrapper.get('[data-testid="copy-health"] [role="status"]').text()).toBe("已复制")
  })

  it("gives accessible Chinese feedback when copying fails", async () => {
    navigator.clipboard.writeText.mockRejectedValueOnce(new Error("blocked"))
    const wrapper = mountGuide()

    await wrapper.get('[data-testid="copy-health"] button').trigger("click")
    await Promise.resolve()
    await Promise.resolve()

    expect(wrapper.get('[data-testid="copy-health"] [role="alert"]').text()).toContain("复制失败")
  })
})
