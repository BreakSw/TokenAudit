import { readStorage, writeStorage } from "./storage"

const KNOWN_COMPLETED_KEY = "tokenauditKnownCompletedAuditIds"
const UNREAD_REPORTS_KEY = "tokenauditUnreadAuditReportIds"
export const AUDIT_READ_STATE_EVENT = "tokenaudit:audit-read-state-changed"

function readIdSet(key) {
  const result = readStorage(key)
  if (!result.ok || !result.value) return { initialized: false, ids: new Set() }
  try {
    const values = JSON.parse(result.value)
    return {
      initialized: true,
      ids: new Set(Array.isArray(values) ? values.map(Number).filter(Number.isFinite) : [])
    }
  } catch {
    return { initialized: false, ids: new Set() }
  }
}

function writeIdSet(key, ids) {
  return writeStorage(key, JSON.stringify([...ids].sort((left, right) => left - right))).ok
}

function announceChange() {
  if (typeof window !== "undefined") window.dispatchEvent(new CustomEvent(AUDIT_READ_STATE_EVENT))
}

export function unreadAuditReportIds() {
  return readIdSet(UNREAD_REPORTS_KEY).ids
}

export function observeAuditCompletions(records) {
  const completed = new Set(
    (Array.isArray(records) ? records : [])
      .filter((record) => record?.status === "completed")
      .map((record) => Number(record.id))
      .filter(Number.isFinite)
  )
  const knownState = readIdSet(KNOWN_COMPLETED_KEY)
  const unread = unreadAuditReportIds()

  if (!knownState.initialized) {
    writeIdSet(KNOWN_COMPLETED_KEY, completed)
    writeIdSet(UNREAD_REPORTS_KEY, unread)
    return unread
  }

  let changed = false
  for (const id of completed) {
    if (!knownState.ids.has(id)) {
      knownState.ids.add(id)
      unread.add(id)
      changed = true
    }
  }
  if (changed) {
    writeIdSet(KNOWN_COMPLETED_KEY, knownState.ids)
    writeIdSet(UNREAD_REPORTS_KEY, unread)
    announceChange()
  }
  return unread
}

export function markAuditReportRead(id) {
  const numericId = Number(id)
  if (!Number.isFinite(numericId)) return unreadAuditReportIds()
  const unread = unreadAuditReportIds()
  if (unread.delete(numericId)) {
    writeIdSet(UNREAD_REPORTS_KEY, unread)
    announceChange()
  }
  return unread
}

export function markAllAuditReportsRead() {
  const unread = unreadAuditReportIds()
  if (unread.size > 0) {
    writeIdSet(UNREAD_REPORTS_KEY, new Set())
    announceChange()
  }
  return new Set()
}
