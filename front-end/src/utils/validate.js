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
