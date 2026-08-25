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

  it("updates a token API URL through the dedicated endpoint", async () => {
    axiosMock.http.put.mockResolvedValueOnce({ data: { id: 9, tokenBaseUrl: "https://relay.example/v1" } })

    const result = await api.updateTokenBaseUrl(9, "https://relay.example/v1")

    expect(axiosMock.http.put).toHaveBeenCalledWith("/api/tokens/9/url", {
      tokenBaseUrl: "https://relay.example/v1"
    })
    expect(result.tokenBaseUrl).toBe("https://relay.example/v1")
  })

  it("deletes an audit through its history endpoint", async () => {
    axiosMock.http.delete.mockResolvedValueOnce({ status: 204 })

    await api.deleteAudit(52)

    expect(axiosMock.http.delete).toHaveBeenCalledWith("/api/audits/52")
  })

  it("cancels a running audit through its task endpoint", async () => {
    axiosMock.http.post.mockResolvedValueOnce({ data: { id: 17, status: "cancelled" } })

    const result = await api.cancelAudit(17)

    expect(axiosMock.http.post).toHaveBeenCalledWith("/api/audits/17/cancel")
    expect(result.status).toBe("cancelled")
  })

  it("starts deep audit through its stable compatibility endpoint", async () => {
    axiosMock.http.post.mockResolvedValueOnce({ data: { auditId: 23, auditMode: "deep" } })

    const result = await api.startDeepAudit({ tokenId: 9, exportFormats: ["json"] })

    expect(axiosMock.http.post).toHaveBeenCalledWith("/api/audits/deep", {
      tokenId: 9,
      exportFormats: ["json"]
    })
    expect(result.auditMode).toBe("deep")
  })
})
