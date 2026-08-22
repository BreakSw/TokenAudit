function auditTimestamp(value) {
  const timestamp = Date.parse(String(value || "").replace(" ", "T"))
  return Number.isNaN(timestamp) ? -Infinity : timestamp
}

export function summarizeDashboard(tokens = [], audits = []) {
  const sortedAudits = [...audits].sort(
    (left, right) => auditTimestamp(right.auditTime) - auditTimestamp(left.auditTime)
  )

  return {
    tokenCount: tokens.length,
    auditCount: audits.length,
    failedCount: audits.filter((audit) => audit.status === "failed").length,
    runningCount: audits.filter((audit) => audit.status === "running").length,
    latestAudit: sortedAudits[0] || null
  }
}
