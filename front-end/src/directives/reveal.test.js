import { beforeEach, describe, expect, it, vi } from "vitest"
import reveal from "./reveal"

describe("reveal directive", () => {
  beforeEach(() => {
    delete window.IntersectionObserver
  })

  it("reveals the element immediately when IntersectionObserver is unavailable", () => {
    const element = document.createElement("section")

    reveal.mounted(element, {})

    expect(element.classList.contains("is-revealed")).toBe(true)
  })

  it("reveals and unobserves an element after it enters the viewport", () => {
    let intersectionCallback
    const unobserve = vi.fn()

    window.IntersectionObserver = vi.fn((callback) => {
      intersectionCallback = callback

      return {
        observe: vi.fn(),
        unobserve,
        disconnect: vi.fn()
      }
    })

    const element = document.createElement("section")
    reveal.mounted(element, {})

    intersectionCallback([{ isIntersecting: true, target: element }])

    expect(element.classList.contains("is-revealed")).toBe(true)
    expect(unobserve).toHaveBeenCalledWith(element)
  })
})
