export function readStorage(key, storage) {
  try {
    const target = storage === undefined ? window.localStorage : storage
    return { ok: true, value: target.getItem(key) }
  } catch {
    return { ok: false, value: null }
  }
}

export function writeStorage(key, value, storage) {
  try {
    const target = storage === undefined ? window.localStorage : storage
    target.setItem(key, value)
    return { ok: true }
  } catch {
    return { ok: false }
  }
}

export function removeStorage(key, storage) {
  try {
    const target = storage === undefined ? window.localStorage : storage
    target.removeItem(key)
    return { ok: true }
  } catch {
    return { ok: false }
  }
}
