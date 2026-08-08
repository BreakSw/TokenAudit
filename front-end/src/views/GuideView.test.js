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

  it("uses an article inside the application main landmark", () => {
    const wrapper = mountGuide()

    expect(wrapper.find("main").exists()).toBe(false)
    expect(wrapper.get('[data-testid="guide-article"]').element.tagName).toBe("ARTICLE")
  })

  it("describes Python as a per-audit child process instead of a third service", () => {
    const wrapper = mountGuide()
    const start = wrapper.get("#start")
    const commands = start.get('[data-testid="copy-start"]')

    expect(start.text()).toContain("无需单独启动审计核心")
    expect(start.text()).toContain("后端按任务执行")
    expect(start.text()).toContain("python -m audit_core")
    expect(commands.text()).toContain("pip install -r requirements.txt")
    expect(commands.text()).not.toContain("python -m audit_core")
    expect(start.text()).not.toContain("终端 1：审计核心")
    expect(start.text()).not.toContain("三个终端")
    expect(wrapper.text()).not.toContain("三个进程")
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

  it("gives every copy action a unique accessible name and does not advertise a missing shortcut", () => {
    const wrapper = mountGuide()
    const copyButtons = wrapper.findAll(".code-toolbar button, .endpoint-heading button")
    const labels = copyButtons.map((button) => button.attributes("aria-label"))

    expect(copyButtons).toHaveLength(8)
    expect(labels.every(Boolean)).toBe(true)
    expect(new Set(labels).size).toBe(copyButtons.length)
    expect(wrapper.find(".search-control kbd").exists()).toBe(false)
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
