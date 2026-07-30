import { afterEach, vi } from "vitest"
import { config, enableAutoUnmount } from "@vue/test-utils"

enableAutoUnmount(afterEach)

config.global.stubs = {
  transition: false,
  "router-link": { template: "<a><slot /></a>" },
  "router-view": { template: "<div />" }
}

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener() {},
    removeListener() {},
    addEventListener() {},
    removeEventListener() {},
    dispatchEvent() { return false }
  })
})

afterEach(() => {
  vi.restoreAllMocks()
  vi.useRealTimers()
  document.body.innerHTML = ""
  localStorage.clear()
})
