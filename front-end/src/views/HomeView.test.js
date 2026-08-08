import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus from "element-plus"
import { createMemoryHistory, createRouter } from "vue-router"
import { afterEach, describe, expect, it, vi } from "vitest"

import HomeView from "./HomeView.vue"
import { listAudits, listTokens } from "../request/api"

vi.mock("../request/api", () => ({
  listAudits: vi.fn(),
  listTokens: vi.fn()
}))

const RouteStub = { template: "<div>route target</div>" }

async function mountHome() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: RouteStub },
      { path: "/audit", component: RouteStub },
      { path: "/tokens", component: RouteStub },
      { path: "/history", component: RouteStub },
      { path: "/report/:id", component: RouteStub }
    ]
  })
  await router.push("/")
  await router.isReady()

  const wrapper = mount(HomeView, {
    global: {
      plugins: [router, ElementPlus],
      directives: { reveal: { mounted() {} } }
    }
  })

  return { router, wrapper }
}

function buttonWithText(wrapper, text) {
  const button = wrapper.findAll("button").find((candidate) => candidate.text().includes(text))
  expect(button, `button ${text}`).toBeTruthy()
  return button
}

function metricValue(wrapper, label) {
  const card = wrapper.findAll(".metric-card").find((candidate) => candidate.text().includes(label))
  expect(card, `metric ${label}`).toBeTruthy()
  return card.get("strong").text()
}

function successfulAudits() {
  return [
    {
      id: 7,
      tokenId: 1,
      status: "completed",
      auditTime: "2026-08-07 09:00:00",
      overallConclusion: "检查通过"
    },
    {
      id: 8,
      tokenId: 2,
      status: "failed",
      auditTime: "2026-08-08 10:30:00",
      overallConclusion: "连接失败"
    }
  ]
}

afterEach(() => {
  vi.clearAllMocks()
})

describe("HomeView dashboard states", () => {
  it("shows loading semantics, then real counts and the latest audit without fabricated values", async () => {
    vi.mocked(listTokens).mockResolvedValue([{ id: 1 }, { id: 2 }])
    vi.mocked(listAudits).mockResolvedValue(successfulAudits())

    const { wrapper } = await mountHome()

    expect(wrapper.get('[role="status"]').text()).toContain("正在同步数据")
    expect(wrapper.get(".status-dot").classes()).toContain("status-dot--loading")

    await flushPromises()

    expect(metricValue(wrapper, "Token 数")).toBe("2")
    expect(metricValue(wrapper, "审计任务")).toBe("2")
    expect(metricValue(wrapper, "运行中")).toBe("0")
    expect(metricValue(wrapper, "失败任务")).toBe("1")
    expect(wrapper.get(".audit-record").text()).toContain("#8")
    expect(wrapper.get(".audit-record").text()).toContain("failed")
    expect(wrapper.get(".audit-record").text()).toContain("连接失败")
    expect(wrapper.get('[role="status"]').text()).toContain("数据更新于")
    expect(wrapper.get(".status-dot").classes()).toContain("status-dot--ready")
    expect(wrapper.text()).not.toContain("72%")
    expect(wrapper.text()).not.toContain("风险评分")
  })

  it("shows a clear empty state with a Token entry action", async () => {
    vi.mocked(listTokens).mockResolvedValue([])
    vi.mocked(listAudits).mockResolvedValue([])

    const { router, wrapper } = await mountHome()
    await flushPromises()

    expect(wrapper.text()).toContain("当前没有可展示的审计数据")
    expect(wrapper.text()).toContain("先录入 Token")
    expect(metricValue(wrapper, "Token 数")).toBe("0")
    expect(metricValue(wrapper, "审计任务")).toBe("0")

    await buttonWithText(wrapper, "录入 Token").trigger("click")
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe("/tokens")
  })

  it("shows an accessible error without stale metrics and recovers after retry", async () => {
    vi.mocked(listTokens).mockRejectedValueOnce(new Error("network down")).mockResolvedValue([{ id: 4 }])
    vi.mocked(listAudits).mockRejectedValueOnce(new Error("network down")).mockResolvedValue([])

    const { wrapper } = await mountHome()
    await flushPromises()

    expect(wrapper.get('[role="alert"]').text()).toContain("仪表盘数据加载失败")
    expect(wrapper.get('[role="alert"]').text()).toContain("无法从服务端获取真实数据")
    expect(wrapper.find(".metrics").exists()).toBe(false)
    expect(wrapper.get('[role="status"]').text()).toContain("数据暂不可用")
    expect(wrapper.get(".status-dot").classes()).toContain("status-dot--error")

    await buttonWithText(wrapper, "重新加载").trigger("click")
    await flushPromises()

    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    expect(metricValue(wrapper, "Token 数")).toBe("1")
    expect(metricValue(wrapper, "审计任务")).toBe("0")
    expect(wrapper.get(".status-dot").classes()).toContain("status-dot--ready")
  })
})

describe("HomeView dashboard navigation", () => {
  it.each([
    ["查看审计报告", "/report/8"],
    ["全部历史 →", "/history"],
    ["发起审计", "/audit"],
    ["管理 Token", "/tokens"]
  ])("navigates from %s to %s", async (label, expectedPath) => {
    vi.mocked(listTokens).mockResolvedValue([{ id: 1 }, { id: 2 }])
    vi.mocked(listAudits).mockResolvedValue(successfulAudits())

    const { router, wrapper } = await mountHome()
    await flushPromises()

    await buttonWithText(wrapper, label).trigger("click")
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe(expectedPath)
  })
})
