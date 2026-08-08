import { beforeEach, describe, expect, it, vi } from "vitest"

const axiosMock = vi.hoisted(() => {
  const state = { requestInterceptor: null }
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
    delete: vi.fn()
  }
  return { http, state }
})

vi.mock("axios", () => ({
  default: {
    create: vi.fn(() => axiosMock.http)
  }
}))

await import("./api")

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
