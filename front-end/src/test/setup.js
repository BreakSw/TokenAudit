import { afterEach } from "vitest"
import { config } from "@vue/test-utils"

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
  document.body.innerHTML = ""
  localStorage.clear()
})
