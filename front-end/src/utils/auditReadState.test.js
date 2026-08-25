import { beforeEach, describe, expect, it, vi } from "vitest"

import {
  markAllAuditReportsRead,
  markAuditReportRead,
  observeAuditCompletions,
  unreadAuditReportIds
} from "./auditReadState"

beforeEach(() => localStorage.clear())

describe("audit report read state", () => {
  it("uses the first completed snapshot as a baseline", () => {
    observeAuditCompletions([{ id: 1, status: "completed" }])
    expect([...unreadAuditReportIds()]).toEqual([])
  })

  it("marks a newly completed audit unread and clears it after viewing", () => {
    observeAuditCompletions([{ id: 2, status: "running" }])
    const event = vi.fn()
    window.addEventListener("tokenaudit:audit-read-state-changed", event)

    observeAuditCompletions([{ id: 2, status: "completed" }])
    expect([...unreadAuditReportIds()]).toEqual([2])

    markAuditReportRead(2)
    expect([...unreadAuditReportIds()]).toEqual([])
    expect(event).toHaveBeenCalledTimes(2)
  })

  it("clears every unread report after opening history", () => {
    observeAuditCompletions([{ id: 1, status: "running" }, { id: 2, status: "running" }])
    observeAuditCompletions([{ id: 1, status: "completed" }, { id: 2, status: "completed" }])
    expect([...unreadAuditReportIds()]).toEqual([1, 2])

    markAllAuditReportsRead()

    expect([...unreadAuditReportIds()]).toEqual([])
  })
})
