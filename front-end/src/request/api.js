import axios from "axios"
import { readStorage } from "../utils/storage"

const http = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8086",
  timeout: 120000
})

http.interceptors.request.use((config) => {
  const { value: key } = readStorage("backendApiKey")
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

export async function startDeepAudit(payload) {
  const { data } = await http.post("/api/audits/deep", payload)
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

export async function cancelAudit(id) {
  const { data } = await http.post(`/api/audits/${id}/cancel`)
  return data
}

export async function updateTokenClaimedModel(id, claimedModel) {
  const { data } = await http.put(`/api/tokens/${id}/model`, { claimedModel })
  return data
}

export async function updateTokenBaseUrl(id, tokenBaseUrl) {
  const { data } = await http.put(`/api/tokens/${id}/url`, { tokenBaseUrl })
  return data
}

export async function deleteAudit(id) {
  await http.delete(`/api/audits/${id}`)
}

export async function getAuditAiConfig() {
  const { data } = await http.get("/api/settings/audit-ai")
  return data
}

export async function saveAuditAiConfig(payload) {
  const { data } = await http.put("/api/settings/audit-ai", payload)
  return data
}

export async function deleteAuditAiConfig() {
  const { data } = await http.delete("/api/settings/audit-ai")
  return data
}
