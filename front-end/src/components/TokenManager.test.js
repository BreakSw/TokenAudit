import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus, { ElMessage, ElMessageBox } from "element-plus"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import TokenManager from "./TokenManager.vue"
import { createToken, deleteToken, listTokens } from "../request/api"

vi.mock("../request/api", () => ({
  createToken: vi.fn(),
  deleteToken: vi.fn(),
  listTokens: vi.fn()
}))

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

function mountTokenManager() {
  const wrapper = mount(TokenManager, {
    attachTo: document.body,
    global: {
      plugins: [ElementPlus],
      directives: { reveal: () => {} }
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

async function fillForm(wrapper, baseUrl = "https://api.example.com") {
  const inputs = wrapper.findAll(".el-input__inner")
  await inputs[0].setValue("生产审计")
  await inputs[1].setValue("sk-secret")
  await inputs[2].setValue("OpenAI 中转")
  await inputs[3].setValue(baseUrl)
  const selects = wrapper.findAllComponents({ name: "ElSelect" })
  await selects[0].setValue("gpt-5.4")
  await selects[1].setValue("gpt-4o-mini")
}

beforeEach(() => {
  vi.mocked(listTokens).mockReset()
  vi.mocked(createToken).mockReset()
  vi.mocked(deleteToken).mockReset()
})

afterEach(() => {
  wrappers.splice(0).forEach((wrapper) => wrapper.unmount())
  document.body.innerHTML = ""
  vi.restoreAllMocks()
})

describe("TokenManager", () => {
  it("shows initial loading before rendering token data", async () => {
    const response = deferred()
    vi.mocked(listTokens).mockReturnValue(response.promise)
    const wrapper = mountTokenManager()

    expect(wrapper.get('[data-testid="token-loading"]').text()).toContain("正在加载")
    expect(wrapper.find('[data-testid="token-table"]').exists()).toBe(false)

    response.resolve([
      { id: 12, name: "生产审计", tokenMasked: "sk-12••••9a", platform: "OpenAI", claimedModel: "gpt-5.4" }
    ])
    await flushPromises()

    expect(wrapper.find('[data-testid="token-loading"]').exists()).toBe(false)
    expect(wrapper.get('[data-testid="token-table"]').text()).toContain("生产审计")
    expect(wrapper.get('[data-testid="token-table"]').text()).toContain("sk-12••••9a")
    expect(wrapper.get(".token-masked").classes()).toContain("token-masked")
  })

  it("separates a true empty state from loading", async () => {
    vi.mocked(listTokens).mockResolvedValue([])
    const wrapper = mountTokenManager()
    await flushPromises()

    expect(wrapper.get('[data-testid="token-empty"]').text()).toContain("暂无 Token")
    expect(wrapper.find('[data-testid="token-table"]').exists()).toBe(false)
  })

  it("keeps load errors visible and retries", async () => {
    vi.mocked(listTokens)
      .mockRejectedValueOnce(new Error("网关暂不可用"))
      .mockResolvedValueOnce([{ id: 3, name: "重试成功", tokenMasked: "sk-***", platform: "中转", claimedModel: "gpt-4o" }])
    const wrapper = mountTokenManager()
    await flushPromises()

    expect(wrapper.get('[data-testid="token-error"]').text()).toContain("网关暂不可用")
    await buttonWithText(wrapper, "重试").trigger("click")
    await flushPromises()

    expect(listTokens).toHaveBeenCalledTimes(2)
    expect(wrapper.find('[data-testid="token-error"]').exists()).toBe(false)
    expect(wrapper.text()).toContain("重试成功")
  })

  it("ignores an older reload that resolves after the latest result", async () => {
    const older = deferred()
    const latest = deferred()
    vi.mocked(listTokens)
      .mockResolvedValueOnce([])
      .mockReturnValueOnce(older.promise)
      .mockReturnValueOnce(latest.promise)
    const wrapper = mountTokenManager()
    await flushPromises()

    const refresh = buttonWithText(wrapper, "刷新")
    refresh.element.click()
    refresh.element.click()
    await flushPromises()
    latest.resolve([{ id: 22, name: "最新 Token", tokenMasked: "new-***", platform: "新平台", claimedModel: "gpt-5.4" }])
    await flushPromises()
    expect(wrapper.text()).toContain("最新 Token")

    older.resolve([{ id: 11, name: "过期 Token", tokenMasked: "old-***", platform: "旧平台", claimedModel: "gpt-4o" }])
    await flushPromises()
    expect(wrapper.text()).toContain("最新 Token")
    expect(wrapper.text()).not.toContain("过期 Token")
  })

  it("does not let an older reload end the latest loading state", async () => {
    const older = deferred()
    const latest = deferred()
    vi.mocked(listTokens)
      .mockResolvedValueOnce([])
      .mockReturnValueOnce(older.promise)
      .mockReturnValueOnce(latest.promise)
    const wrapper = mountTokenManager()
    await flushPromises()

    const refresh = buttonWithText(wrapper, "刷新")
    refresh.element.click()
    refresh.element.click()
    await flushPromises()
    older.resolve([])
    await flushPromises()
    expect(wrapper.get('[data-testid="token-loading"]').text()).toContain("正在加载")

    latest.resolve([])
    await flushPromises()
    expect(wrapper.find('[data-testid="token-loading"]').exists()).toBe(false)
  })

  it("does not toast or apply a pending reload after unmount", async () => {
    const response = deferred()
    vi.mocked(listTokens).mockReturnValue(response.promise)
    const errorToast = vi.spyOn(ElMessage, "error")
    const wrapper = mountTokenManager()
    wrapper.unmount()

    response.reject(new Error("late failure"))
    await flushPromises()
    expect(errorToast).not.toHaveBeenCalled()
  })

  it("shows validation feedback inside the form", async () => {
    vi.mocked(listTokens).mockResolvedValue([])
    const wrapper = mountTokenManager()
    await flushPromises()

    await buttonWithText(wrapper, "保存 Token").trigger("click")

    expect(wrapper.get('[data-testid="form-error"]').text()).toContain("请补全必填项")
    expect(createToken).not.toHaveBeenCalled()
  })

  it("saves a valid service root, resets the form and reloads the workspace", async () => {
    vi.mocked(listTokens)
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([{ id: 31, name: "生产审计", tokenMasked: "sk-***", platform: "OpenAI 中转", claimedModel: "gpt-5.4" }])
    vi.mocked(createToken).mockResolvedValue({ id: 31 })
    const wrapper = mountTokenManager()
    await flushPromises()
    await fillForm(wrapper)

    await buttonWithText(wrapper, "保存 Token").trigger("click")
    await flushPromises()

    expect(createToken).toHaveBeenCalledWith({
      name: "生产审计",
      token: "sk-secret",
      platform: "OpenAI 中转",
      tokenBaseUrl: "https://api.example.com",
      claimedModel: "gpt-5.4",
      nonClaimedModel: "gpt-4o-mini"
    })
    expect(listTokens).toHaveBeenCalledTimes(2)
    expect(wrapper.text()).toContain("生产审计")
    expect(wrapper.findAll(".el-input__inner")[0].element.value).toBe("")
  })

  it("rejects an endpoint URL with persistent feedback before create", async () => {
    vi.mocked(listTokens).mockResolvedValue([])
    const wrapper = mountTokenManager()
    await flushPromises()
    await fillForm(wrapper, "https://api.example.com/v1/chat/completions")

    await buttonWithText(wrapper, "保存 Token").trigger("click")

    expect(wrapper.get('[data-testid="form-error"]').text()).toContain("服务根地址")
    expect(createToken).not.toHaveBeenCalled()
  })

  it("does not toast when a pending save rejects after unmount", async () => {
    const response = deferred()
    vi.mocked(listTokens).mockResolvedValue([])
    vi.mocked(createToken).mockReturnValue(response.promise)
    const errorToast = vi.spyOn(ElMessage, "error")
    const wrapper = mountTokenManager()
    await flushPromises()
    await fillForm(wrapper)
    await buttonWithText(wrapper, "保存 Token").trigger("click")
    wrapper.unmount()

    response.reject(new Error("late save failure"))
    await flushPromises()
    expect(errorToast).not.toHaveBeenCalled()
  })

  it("preserves delete cancellation and refreshes visible data after confirmation", async () => {
    const token = { id: 8, name: "待删除", tokenMasked: "sk-***", platform: "代理", claimedModel: "gpt-4o" }
    vi.mocked(listTokens).mockResolvedValueOnce([token]).mockResolvedValueOnce([])
    vi.mocked(deleteToken).mockResolvedValue({})
    const confirm = vi.spyOn(ElMessageBox, "confirm")
    confirm.mockRejectedValueOnce("cancel").mockResolvedValueOnce("confirm")
    const wrapper = mountTokenManager()
    await flushPromises()

    await buttonWithText(wrapper, "删除").trigger("click")
    await flushPromises()
    expect(deleteToken).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain("待删除")

    await buttonWithText(wrapper, "删除").trigger("click")
    await flushPromises()
    expect(deleteToken).toHaveBeenCalledWith(8)
    expect(wrapper.get('[data-testid="token-empty"]').text()).toContain("暂无 Token")
  })

  it("surfaces an unexpected confirmation failure instead of treating it as cancellation", async () => {
    const token = { id: 18, name: "保留项", tokenMasked: "sk-***", platform: "代理", claimedModel: "gpt-4o" }
    vi.mocked(listTokens).mockResolvedValue([token])
    const failure = new Error("确认服务异常")
    vi.spyOn(ElMessageBox, "confirm").mockRejectedValue(failure)
    const errorToast = vi.spyOn(ElMessage, "error")
    const wrapper = mountTokenManager()
    await flushPromises()

    await buttonWithText(wrapper, "删除").trigger("click")
    await flushPromises()

    expect(wrapper.get('[data-testid="operation-error"]').text()).toContain("确认服务异常")
    expect(errorToast).toHaveBeenCalledWith("确认服务异常")
    expect(deleteToken).not.toHaveBeenCalled()
  })

  it("does not toast when a pending delete rejects after unmount", async () => {
    const response = deferred()
    const token = { id: 28, name: "卸载项", tokenMasked: "sk-***", platform: "代理", claimedModel: "gpt-4o" }
    vi.mocked(listTokens).mockResolvedValue([token])
    vi.mocked(deleteToken).mockReturnValue(response.promise)
    vi.spyOn(ElMessageBox, "confirm").mockResolvedValue("confirm")
    const errorToast = vi.spyOn(ElMessage, "error")
    const wrapper = mountTokenManager()
    await flushPromises()
    await buttonWithText(wrapper, "删除").trigger("click")
    await flushPromises()
    wrapper.unmount()

    response.reject(new Error("late delete failure"))
    await flushPromises()
    expect(errorToast).not.toHaveBeenCalled()
  })
})
