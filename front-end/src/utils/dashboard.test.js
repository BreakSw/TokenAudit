import { describe, expect, it } from "vitest"
import { summarizeDashboard } from "./dashboard"

describe("summarizeDashboard", () => {
  it("summarizes tokens and audits while selecting the latest audit", () => {
    const tokens = [{ id: 1 }, { id: 2 }]
    const audits = [
      { id: 7, status: "completed", auditTime: "2026-08-07 09:00:00" },
      { id: 8, status: "failed", auditTime: "2026-08-08 10:30:00" }
    ]

    expect(summarizeDashboard(tokens, audits)).toEqual({
      tokenCount: 2,
      auditCount: 2,
      failedCount: 1,
      runningCount: 0,
      latestAudit: audits[1]
    })
  })

  it("returns strict zero values and null for empty inputs", () => {
    expect(summarizeDashboard([], [])).toEqual({
      tokenCount: 0,
      auditCount: 0,
      failedCount: 0,
      runningCount: 0,
      latestAudit: null
    })
  })
})
