import { describe, expect, it } from "vitest"

import { GUIDE_SECTIONS, searchGuideSections } from "./guide"

describe("guide search", () => {
  it("matches Chinese titles and API keywords", () => {
    expect(searchGuideSections("环境变量").map((item) => item.id)).toContain("configure")
    expect(searchGuideSections("POST /api/audits").map((item) => item.id)).toContain("run-audit")
  })

  it("normalizes surrounding whitespace and letter case", () => {
    expect(searchGuideSections("  api  ").length).toBeGreaterThan(0)
    expect(searchGuideSections("MODEL").map((item) => item.id)).toContain("token")
  })

  it("returns all sections for an empty query and no fake match otherwise", () => {
    expect(searchGuideSections("")).toEqual(GUIDE_SECTIONS)
    expect(searchGuideSections("不存在的章节")).toEqual([])
  })
})
