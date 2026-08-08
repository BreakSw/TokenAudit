import { flushPromises, mount } from "@vue/test-utils"
import ElementPlus, { ElMessageBox } from "element-plus"
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

  it("shows validation feedback inside the form", async () => {
    vi.mocked(listTokens).mockResolvedValue([])
    const wrapper = mountTokenManager()
    await flushPromises()

    await buttonWithText(wrapper, "保存 Token").trigger("click")

    expect(wrapper.get('[data-testid="form-error"]').text()).toContain("请补全必填项")
    expect(createToken).not.toHaveBeenCalled()
  })

  it("preserves delete cancellation and refreshes visible data after confirmation", async () => {
    const token = { id: 8, name: "待删除", tokenMasked: "sk-***", platform: "代理", claimedModel: "gpt-4o" }
    vi.mocked(listTokens).mockResolvedValueOnce([token]).mockResolvedValueOnce([])
    vi.mocked(deleteToken).mockResolvedValue({})
    const confirm = vi.spyOn(ElMessageBox, "confirm")
    confirm.mockRejectedValueOnce(new Error("cancel")).mockResolvedValueOnce("confirm")
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
})
