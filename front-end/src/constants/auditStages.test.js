import { describe, expect, it } from "vitest"
import { AUDIT_STAGES, stageIndex, stageLabel } from "./auditStages"

describe("audit stages", () => {
  it("defines the canonical audit stage order", () => {
    expect(AUDIT_STAGES.map((stage) => stage.key)).toEqual([
      "validity",
      "permission",
      "watering",
      "compliance",
      "stability",
      "security",
      "overall"
    ])
  })

  it("resolves stage indexes and labels with safe fallbacks", () => {
    expect(stageIndex("security")).toBe(5)
    expect(stageLabel("security")).toBe("安全性审计")
    expect(stageIndex("unknown")).toBe(0)
    expect(stageLabel("unknown")).toBe("-")
  })
})
