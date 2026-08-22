import { describe, expect, it } from "vitest"

import { isBaseUrl, isUrl } from "./validate"

describe("URL validation", () => {
  it("keeps generic URL validation available", () => {
    expect(isUrl("https://api.example.com/v1?mode=test")).toBe(true)
  })

  it.each([
    "https://api.example.com",
    "https://api.example.com/",
    "https://openrouter.ai/api/v1",
    "https://api.example.com/compatible-mode/v1/",
    "https://api.example.com/v1/chat/completions",
    "https://api.example.com/v1/responses",
    "https://api.perplexity.ai/chat/completions",
    "http://localhost:8081"
  ])("accepts a HTTP(S) API base URL: %s", (value) => {
    expect(isBaseUrl(value)).toBe(true)
  })

  it.each([
    "https://api.example.com/v1/models",
    "https://api.example.com?tenant=1",
    "https://api.example.com/#docs",
    "https://user:secret@api.example.com",
    "ftp://api.example.com",
    "not a url"
  ])("rejects a non-inference endpoint or unsafe API URL: %s", (value) => {
    expect(isBaseUrl(value)).toBe(false)
  })
})
