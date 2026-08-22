import { describe, expect, it, vi } from "vitest"

async function loadStorageUtils() {
  return import("./storage.js")
}

describe("safe storage helpers", () => {
  it("distinguishes a missing value from a read failure", async () => {
    const { readStorage } = await loadStorageUtils()
    const missingStorage = { getItem: vi.fn(() => null) }
    const blockedStorage = {
      getItem: vi.fn(() => {
        throw new DOMException("blocked", "SecurityError")
      })
    }

    expect(readStorage("missing", missingStorage)).toEqual({ ok: true, value: null })
    expect(readStorage("blocked", blockedStorage)).toEqual({ ok: false, value: null })
  })

  it("returns values without changing them", async () => {
    const { readStorage } = await loadStorageUtils()
    const storage = { getItem: vi.fn(() => "saved-value") }

    expect(readStorage("key", storage)).toEqual({ ok: true, value: "saved-value" })
  })

  it("reports write and removal success without throwing", async () => {
    const { removeStorage, writeStorage } = await loadStorageUtils()
    const workingStorage = { setItem: vi.fn(), removeItem: vi.fn() }
    const blockedStorage = {
      setItem: vi.fn(() => {
        throw new DOMException("blocked", "SecurityError")
      }),
      removeItem: vi.fn(() => {
        throw new DOMException("blocked", "SecurityError")
      })
    }

    expect(writeStorage("key", "value", workingStorage)).toEqual({ ok: true })
    expect(removeStorage("key", workingStorage)).toEqual({ ok: true })
    expect(writeStorage("key", "value", blockedStorage)).toEqual({ ok: false })
    expect(removeStorage("key", blockedStorage)).toEqual({ ok: false })
  })

  it("does not throw when the browser storage object itself is unavailable", async () => {
    const { readStorage } = await loadStorageUtils()
    vi.spyOn(window, "localStorage", "get").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError")
    })

    expect(readStorage("key")).toEqual({ ok: false, value: null })
  })
})
