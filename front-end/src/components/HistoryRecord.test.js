import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus, { ElMessage } from "element-plus"
import { createMemoryHistory, createRouter } from "vue-router"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import HistoryRecord from "./HistoryRecord.vue"
import { listAudits } from "../request/api"

vi.mock("../request/api", () => ({ listAudits: vi.fn() }))

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

async function mountHistoryRecord() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/history", component: HistoryRecord },
      { path: "/audit", component: { template: "<div>audit route</div>" } },
      { path: "/report/:id", component: { template: "<div>report route</div>" } }
    ]
  })
  await router.push("/history")
  await router.isReady()
  const wrapper = mount(HistoryRecord, {
    attachTo: document.body,
    global: {
      plugins: [router, ElementPlus],
      directives: { reveal: () => {} }
    }
  })
  wrappers.push(wrapper)
  return { wrapper, router }
}

function buttonWithText(wrapper, text) {
  const button = wrapper.findAll("button").find((candidate) => candidate.text().trim() === text)
  expect(button, `button ${text}`).toBeTruthy()
  return button
}

beforeEach(() => vi.mocked(listAudits).mockReset())

afterEach(() => {
  wrappers.splice(0).forEach((wrapper) => wrapper.unmount())
  document.body.innerHTML = ""
  vi.restoreAllMocks()
})

describe("HistoryRecord", () => {
  it("shows loading, then audit fields and report navigation", async () => {
    const response = deferred()
    vi.mocked(listAudits).mockReturnValue(response.promise)
    const { wrapper, router } = await mountHistoryRecord()

    expect(wrapper.get('[data-testid="history-loading"]').text()).toContain("正在加载")
    response.resolve([{
      id: 42,
      tokenId: 7,
      auditTime: "2026-08-08 16:30:00",
      status: "completed",
      progress: 100,
      overallConclusion: "该 Token 的模型身份与宣称一致，但需要持续观察配额策略。"
    }])
    await flushPromises()

    const table = wrapper.get('[data-testid="history-table"]')
    expect(table.text()).toContain("42")
    expect(table.text()).toContain("7")
    expect(table.text()).toContain("2026-08-08 16:30:00")
    expect(table.text()).toContain("completed")
    expect(table.text()).toContain("100%")
    expect(wrapper.get(".conclusion-text").attributes("title")).toContain("模型身份与宣称一致")
    expect(wrapper.get(".status-badge--completed").exists()).toBe(true)

    await buttonWithText(wrapper, "查看报告").trigger("click")
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe("/report/42")
  })

  it("renders a real empty state that can start a new audit", async () => {
    vi.mocked(listAudits).mockResolvedValue([])
    const { wrapper, router } = await mountHistoryRecord()
    await flushPromises()

    expect(wrapper.get('[data-testid="history-empty"]').text()).toContain("暂无审计记录")
    expect(wrapper.find('[data-testid="history-table"]').exists()).toBe(false)
    await buttonWithText(wrapper, "发起审计").trigger("click")
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe("/audit")
  })

  it("keeps errors visible and retries", async () => {
    vi.mocked(listAudits)
      .mockRejectedValueOnce(new Error("历史服务离线"))
      .mockResolvedValueOnce([{ id: 9, tokenId: 2, auditTime: "now", status: "running", progress: 35, overallConclusion: "执行中" }])
    const { wrapper } = await mountHistoryRecord()
    await flushPromises()

    expect(wrapper.get('[data-testid="history-error"]').text()).toContain("历史服务离线")
    await buttonWithText(wrapper, "重试").trigger("click")
    await flushPromises()

    expect(listAudits).toHaveBeenCalledTimes(2)
    expect(wrapper.find('[data-testid="history-error"]').exists()).toBe(false)
    expect(wrapper.get(".status-badge--running").text()).toContain("running")
  })

  it("ignores an older reload that resolves after the latest result", async () => {
    const older = deferred()
    const latest = deferred()
    vi.mocked(listAudits)
      .mockResolvedValueOnce([])
      .mockReturnValueOnce(older.promise)
      .mockReturnValueOnce(latest.promise)
    const { wrapper } = await mountHistoryRecord()
    await flushPromises()

    const refresh = buttonWithText(wrapper, "刷新记录")
    refresh.element.click()
    refresh.element.click()
    await flushPromises()
    latest.resolve([{ id: 72, tokenId: 7, auditTime: "latest", status: "completed", progress: 100, overallConclusion: "最新审计" }])
    await flushPromises()
    older.resolve([{ id: 61, tokenId: 6, auditTime: "older", status: "failed", progress: 20, overallConclusion: "过期审计" }])
    await flushPromises()

    expect(wrapper.text()).toContain("最新审计")
    expect(wrapper.text()).not.toContain("过期审计")
  })

  it("keeps loading for the newest request when an older reload finishes", async () => {
    const older = deferred()
    const latest = deferred()
    vi.mocked(listAudits)
      .mockResolvedValueOnce([])
      .mockReturnValueOnce(older.promise)
      .mockReturnValueOnce(latest.promise)
    const { wrapper } = await mountHistoryRecord()
    await flushPromises()

    const refresh = buttonWithText(wrapper, "刷新记录")
    refresh.element.click()
    refresh.element.click()
    await flushPromises()
    older.resolve([])
    await flushPromises()
    expect(wrapper.get('[data-testid="history-loading"]').text()).toContain("正在加载")

    latest.resolve([])
    await flushPromises()
    expect(wrapper.find('[data-testid="history-loading"]').exists()).toBe(false)
  })

  it("does not toast or apply a pending reload after unmount", async () => {
    const response = deferred()
    vi.mocked(listAudits).mockReturnValue(response.promise)
    const errorToast = vi.spyOn(ElMessage, "error")
    const { wrapper } = await mountHistoryRecord()
    wrapper.unmount()

    response.reject(new Error("late history failure"))
    await flushPromises()
    expect(errorToast).not.toHaveBeenCalled()
  })
})
