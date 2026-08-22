export function required(v) {
  return v !== null && v !== undefined && String(v).trim().length > 0
}

export function isUrl(v) {
  try {
    const u = new URL(String(v))
    return u.protocol === "http:" || u.protocol === "https:"
  } catch {
    return false
  }
}

export function isBaseUrl(v) {
  const value = String(v ?? "").trim()
  if (!isUrl(value) || /[?#]/.test(value)) return false
  try {
    const url = new URL(value)
    if (url.username || url.password) return false
    const path = decodeURIComponent(url.pathname).replace(/\/+$/, "")
    if (path.split("/").some((segment) => segment === "." || segment === "..")) return false
    const normalized = path.toLowerCase()
    return !normalized.endsWith("/models")
  } catch {
    return false
  }
}
