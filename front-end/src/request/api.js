import axios from "axios"

const http = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8081",
  timeout: 120000
})

http.interceptors.request.use((config) => {
  const key = localStorage.getItem("backendApiKey")
  if (key) {
    config.headers["X-API-KEY"] = key
  }
  return config
})

export async function listTokens() {
  const { data } = await http.get("/api/tokens")
  return data
}

export async function createToken(payload) {
  const { data } = await http.post("/api/tokens", payload)
  return data
}

export async function deleteToken(id) {
  const { data } = await http.delete(`/api/tokens/${id}`)
  return data
}

export async function startAudit(payload) {
  const { data } = await http.post("/api/audits", payload)
  return data
}

export async function getAudit(id) {
  const { data } = await http.get(`/api/audits/${id}`)
  return data
}

export async function listAudits(tokenId) {
  const { data } = await http.get("/api/audits", { params: tokenId ? { tokenId } : {} })
  return data
}

export async function listAuditEvents(id) {
  const { data } = await http.get(`/api/audits/${id}/events`)
  return data
}
