import { beforeEach, describe, expect, it, vi } from "vitest"

const axiosMock = vi.hoisted(() => {
  const state = { requestInterceptor: null, createOptions: null }
  const http = {
    interceptors: {
      request: {
        use: vi.fn((callback) => {
          state.requestInterceptor = callback
        })
      }
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
  const create = vi.fn((options) => {
    state.createOptions = options
    return http
  })
  return { create, http, state }
})

vi.mock("axios", () => ({
  default: {
    create: axiosMock.create
  }
}))

const api = await import("./api")

describe("API key request interceptor", () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it("adds the stored API key through the registered interceptor callback", () => {
    localStorage.setItem("backendApiKey", "stored-key")
    const config = { headers: { Accept: "application/json" } }

    const result = axiosMock.state.requestInterceptor(config)

    expect(result).toBe(config)
    expect(result.headers).toEqual({ Accept: "application/json", "X-API-KEY": "stored-key" })
  })

  it("continues without an API key when storage access is blocked", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError")
    })
    const config = { headers: { Accept: "application/json" } }
    let result

    expect(() => {
      result = axiosMock.state.requestInterceptor(config)
    }).not.toThrow()
    expect(result).toBe(config)
    expect(config.headers).toEqual({ Accept: "application/json" })
  })
})

describe("API client defaults", () => {
  it("targets the backend's actual default port", () => {
    expect(axiosMock.state.createOptions).toEqual(expect.objectContaining({
      baseURL: "http://localhost:8086"
    }))
  })

  it("updates a token model through the dedicated endpoint", async () => {
    axiosMock.http.put.mockResolvedValueOnce({ data: { id: 9, claimedModel: "vendor/new-model" } })

    const result = await api.updateTokenClaimedModel(9, "vendor/new-model")

    expect(axiosMock.http.put).toHaveBeenCalledWith("/api/tokens/9/model", {
      claimedModel: "vendor/new-model"
    })
    expect(result.claimedModel).toBe("vendor/new-model")
  })

  it("cancels a running audit through its task endpoint", async () => {
    axiosMock.http.post.mockResolvedValueOnce({ data: { id: 17, status: "cancelled" } })

    const result = await api.cancelAudit(17)

    expect(axiosMock.http.post).toHaveBeenCalledWith("/api/audits/17/cancel")
    expect(result.status).toBe("cancelled")
  })
})
