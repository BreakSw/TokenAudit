<template>
  <div class="console-shell">
    <aside class="console-sidebar" aria-label="主导航">
      <RouterLink class="brand-block" to="/home" aria-label="返回 TokenAudit 项目主页">
        <div class="brand-mark" aria-hidden="true"><img src="/favicon.svg" alt="" /></div>
        <div class="brand-copy">
          <div class="brand-name">TokenAudit</div>
          <div class="brand-meta">安全审计控制台</div>
        </div>
        <span class="brand-arrow" aria-hidden="true">↗</span>
      </RouterLink>

      <div class="system-state" aria-label="系统状态">
        <span class="state-indicator" aria-hidden="true" />
        <span>审计服务待命</span>
        <span class="state-code">LOCAL</span>
      </div>

      <nav class="primary-nav">
        <div class="nav-label">工作区</div>
        <RouterLink
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'is-active': activePath === item.path }"
          :aria-current="activePath === item.path ? 'page' : undefined"
          @click="item.path === '/history' && acknowledgeHistoryNotifications()"
        >
          <span class="nav-index">{{ item.index }}</span>
          <span>{{ item.label }}</span>
          <span
            v-if="item.path === '/history' && hasUnreadAuditReports"
            class="nav-unread-dot"
            data-testid="history-unread-dot"
            :aria-label="`${unreadAuditCount} 份新审计报告未查看`"
          />
        </RouterLink>
      </nav>

      <div class="sidebar-foot">
        <span>节点</span>
        <span class="mono">127.0.0.1</span>
      </div>
    </aside>

    <section class="console-workspace">
      <header class="console-header">
        <div class="header-heading">
          <span class="header-eyebrow">TOKEN AUDIT / {{ sectionIndex }}</span>
          <h1>{{ currentTitle }}</h1>
        </div>

        <div class="header-actions">
          <div class="environment-state" aria-label="运行环境为本地">
            <span class="state-indicator" aria-hidden="true" />
            <span class="environment-label">运行环境</span>
            <span class="mono">LOCAL</span>
          </div>
          <el-button class="settings-button" size="small" @click="openSettings()">
            设置
          </el-button>
        </div>
      </header>

      <nav class="mobile-nav" aria-label="移动端主导航">
        <RouterLink
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          class="mobile-nav-item"
          :class="{ 'is-active': activePath === item.path }"
          :aria-current="activePath === item.path ? 'page' : undefined"
          @click="item.path === '/history' && acknowledgeHistoryNotifications()"
        >
          <span>{{ item.index }}</span>
          <span>{{ item.shortLabel }}</span>
          <span v-if="item.path === '/history' && hasUnreadAuditReports" class="mobile-unread-dot" aria-hidden="true" />
        </RouterLink>
      </nav>

      <main class="console-main">
        <div class="main-frame">
          <router-view />
        </div>
      </main>
    </section>

    <el-drawer
      v-model="settingsOpen"
      class="settings-drawer"
      size="520px"
      title="控制台设置"
      :with-header="true"
      @closed="discardSettings"
    >
      <div class="settings-wrap">
        <section class="settings-section">
          <div class="settings-section-head">
            <div>
              <div class="settings-kicker">BACKEND ACCESS</div>
              <div class="settings-title">后端访问</div>
            </div>
            <span class="settings-status is-local">浏览器本地</span>
          </div>
          <p class="settings-subtitle">仅当后端启用了 X-API-KEY 校验时填写。此项只保存在当前浏览器。</p>
          <label class="settings-field-label" for="backend-api-key">X-API-KEY</label>
          <el-input id="backend-api-key" v-model="backendApiKey" placeholder="可选" size="large" clearable show-password />
          <p v-if="storageError" class="settings-error" role="alert" aria-live="assertive">{{ storageError }}</p>
          <div class="settings-actions compact">
            <el-button @click="clearKey">清除</el-button>
            <el-button type="primary" @click="saveKey">保存</el-button>
          </div>
        </section>

        <section class="settings-section audit-ai-section" :class="{ 'is-focused': settingsFocus === 'audit-ai' }">
          <div class="settings-section-head">
            <div>
              <div class="settings-kicker">AUDIT AI</div>
              <div class="settings-title">审计判定模型</div>
            </div>
            <span class="settings-status" :class="auditAiConfigured ? 'is-ready' : 'is-empty'">
              {{ auditAiConfigured ? '已配置' : '未配置' }}
            </span>
          </div>
          <p class="settings-subtitle">支持任意 OpenAI Chat Completions 兼容服务。API Key 加密保存于 Redis，不会写入浏览器。</p>

          <div v-if="settingsPrompt" class="settings-prompt" role="alert" aria-live="assertive">
            <span class="state-indicator" aria-hidden="true" />
            {{ settingsPrompt }}
          </div>

          <div class="settings-grid">
            <div class="settings-field full">
              <label class="settings-field-label" for="audit-ai-provider">服务商</label>
              <el-select id="audit-ai-provider" v-model="auditAi.provider" size="large" filterable allow-create popper-class="audit-ai-provider-popper" @change="applyProviderPreset">
                <el-option-group v-for="group in auditAiProviderGroups" :key="group.label" :label="group.label">
                  <el-option v-for="provider in group.providers" :key="provider.name" :label="provider.name" :value="provider.name" />
                </el-option-group>
              </el-select>
              <span class="field-hint">仅提供模型厂商官方接口，共 {{ auditAiProviders.length }} 项；审计判定不会经过第三方中转站。</span>
            </div>
            <div class="settings-field full">
              <label class="settings-field-label" for="audit-ai-url">API URL</label>
              <el-input id="audit-ai-url" v-model="auditAi.apiUrl" size="large" placeholder="https://.../v1/chat/completions" />
            </div>
            <div class="settings-field full">
              <label class="settings-field-label" for="audit-ai-model">模型</label>
              <el-input id="audit-ai-model" v-model="auditAi.model" size="large" placeholder="例如 openai/gpt-4o-mini" />
            </div>
            <div class="settings-field full">
              <label class="settings-field-label" for="audit-ai-key">API Key</label>
              <el-input id="audit-ai-key" v-model="auditAi.apiKey" size="large" show-password clearable :placeholder="auditAiConfigured ? '已配置，留空则保留原密钥' : '请输入审计 API Key'" />
              <span v-if="auditAiMasked" class="field-hint">当前密钥：{{ auditAiMasked }}</span>
            </div>
            <div class="settings-field ttl-value">
              <label class="settings-field-label" for="audit-ai-ttl">有效期</label>
              <el-input-number id="audit-ai-ttl" v-model="auditAi.ttlValue" :min="1" :max="43200" controls-position="right" size="large" />
            </div>
            <div class="settings-field ttl-unit">
              <label class="settings-field-label" for="audit-ai-ttl-unit">单位</label>
              <el-select id="audit-ai-ttl-unit" v-model="auditAi.ttlUnit" size="large">
                <el-option label="分钟" value="minute" />
                <el-option label="小时" value="hour" />
                <el-option label="天" value="day" />
              </el-select>
            </div>
          </div>

          <div class="settings-note">
            {{ auditAiConfigured ? `剩余有效期 ${auditAiExpiresText}。` : '尚未保存审计 AI 配置。' }}
            每次保存都会从当前设定重新计算 Redis 过期时间。
          </div>
          <p v-if="auditAiError" class="settings-error" role="alert" aria-live="assertive">{{ auditAiError }}</p>
          <div class="settings-actions compact">
            <el-button v-if="auditAiConfigured" :loading="auditAiSaving" @click="removeAuditAiConfig">删除配置</el-button>
            <el-button type="primary" :loading="auditAiSaving" @click="persistAuditAiConfig">保存审计配置</el-button>
          </div>
        </section>

        <div class="settings-actions drawer-actions">
          <el-button size="large" @click="closeSettings">关闭</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, provide, reactive, ref, watch } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { ElMessage } from "element-plus"
import { deleteAuditAiConfig, getAuditAiConfig, listAudits, saveAuditAiConfig } from "./request/api"
import { readStorage, removeStorage, writeStorage } from "./utils/storage"
import {
  AUDIT_READ_STATE_EVENT,
  markAllAuditReportsRead,
  markAuditReportRead,
  observeAuditCompletions,
  unreadAuditReportIds
} from "./utils/auditReadState"

const navigation = [
  { path: "/", label: "审计控制台", shortLabel: "控制台", index: "00" },
  { path: "/audit", label: "快速审计", shortLabel: "快速", index: "01" },
  { path: "/audit/deep", label: "深度审计", shortLabel: "深度", index: "02" },
  { path: "/tokens", label: "Token 管理", shortLabel: "Token", index: "03" },
  { path: "/history", label: "历史记录", shortLabel: "历史", index: "04" },
  { path: "/guide", label: "使用文档", shortLabel: "文档", index: "05" }
]

const route = useRoute()
const backendApiKey = ref("")
const settingsOpen = ref(false)
const storageError = ref("")
const settingsFocus = ref("")
const settingsPrompt = ref("")
const auditAiConfigured = ref(false)
const auditAiMasked = ref("")
const auditAiExpiresInSeconds = ref(0)
const auditAiSaving = ref(false)
const auditAiError = ref("")
const unreadAuditCount = ref(0)
const hasUnreadAuditReports = computed(() => unreadAuditCount.value > 0)
let auditCompletionTimer = null
let auditCompletionRequest = null
const auditAi = reactive({
  provider: "DeepSeek",
  apiUrl: "https://api.deepseek.com/v1/chat/completions",
  model: "deepseek-chat",
  apiKey: "",
  ttlValue: 24,
  ttlUnit: "hour"
})
const auditAiProviderGroups = [
  {
    label: "国际官方模型",
    providers: [
      { name: "OpenAI / GPT", apiUrl: "https://api.openai.com/v1/chat/completions", model: "gpt-4o-mini" },
      { name: "Anthropic / Claude", apiUrl: "https://api.anthropic.com/v1/chat/completions", model: "claude-sonnet-4-5" },
      { name: "Google / Gemini", apiUrl: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", model: "gemini-2.5-flash" },
      { name: "xAI / Grok", apiUrl: "https://api.x.ai/v1/chat/completions", model: "grok-3-mini" },
      { name: "Mistral AI", apiUrl: "https://api.mistral.ai/v1/chat/completions", model: "mistral-small-latest" },
      { name: "Cohere", apiUrl: "https://api.cohere.com/compatibility/v1/chat/completions", model: "command-r-plus" },
      { name: "Perplexity", apiUrl: "https://api.perplexity.ai/chat/completions", model: "sonar" }
    ]
  },
  {
    label: "国内官方模型",
    providers: [
      { name: "DeepSeek", apiUrl: "https://api.deepseek.com/v1/chat/completions", model: "deepseek-chat" },
      { name: "Moonshot / Kimi", apiUrl: "https://api.moonshot.cn/v1/chat/completions", model: "moonshot-v1-8k" },
      { name: "阿里云百炼 / 通义千问", apiUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", model: "qwen-plus" },
      { name: "智谱 AI / GLM", apiUrl: "https://open.bigmodel.cn/api/paas/v4/chat/completions", model: "glm-4-flash" },
      { name: "火山方舟 / 豆包", apiUrl: "https://ark.cn-beijing.volces.com/api/v3/chat/completions", model: "" },
      { name: "腾讯混元", apiUrl: "https://api.hunyuan.cloud.tencent.com/v1/chat/completions", model: "hunyuan-turbos-latest" },
      { name: "百度千帆 / 文心", apiUrl: "https://qianfan.baidubce.com/v2/chat/completions", model: "ernie-speed-128k" },
      { name: "MiniMax", apiUrl: "https://api.minimaxi.com/v1/chat/completions", model: "MiniMax-Text-01" },
      { name: "零一万物 / Yi", apiUrl: "https://api.lingyiwanwu.com/v1/chat/completions", model: "yi-lightning" },
      { name: "阶跃星辰 / StepFun", apiUrl: "https://api.stepfun.com/v1/chat/completions", model: "step-2-16k" },
      { name: "百川智能", apiUrl: "https://api.baichuan-ai.com/v1/chat/completions", model: "Baichuan4" }
    ]
  },
  {
    label: "官方云部署与自定义",
    providers: [
      { name: "Azure OpenAI（填写部署 URL）", apiUrl: "", model: "" },
      { name: "Google Vertex AI / Gemini（填写项目 URL）", apiUrl: "", model: "" },
      { name: "自定义官方 OpenAI 兼容接口", apiUrl: "", model: "" }
    ]
  }
]
const auditAiProviders = computed(() => auditAiProviderGroups.flatMap((group) => group.providers))

function syncUnreadAuditCount() {
  unreadAuditCount.value = unreadAuditReportIds().size
}

function acknowledgeHistoryNotifications() {
  markAllAuditReportsRead()
  syncUnreadAuditCount()
}

async function pollAuditCompletions() {
  if (auditCompletionRequest) return auditCompletionRequest
  auditCompletionRequest = listAudits()
    .then((records) => {
      observeAuditCompletions(records)
      const viewedReport = /^\/report\/(\d+)/.exec(route.fullPath)
      if (viewedReport) markAuditReportRead(Number(viewedReport[1]))
      if (route.path === "/history") markAllAuditReportsRead()
      syncUnreadAuditCount()
    })
    .catch(() => {})
    .finally(() => {
      auditCompletionRequest = null
    })
  return auditCompletionRequest
}

const isReportRoute = computed(() => route.path.startsWith("/report/"))
const activePath = computed(() => (isReportRoute.value ? "/history" : route.path))
const currentNavigation = computed(() => navigation.find((item) => item.path === activePath.value))
const currentTitle = computed(() => (
  isReportRoute.value
    ? "审计报告"
    : route.meta.title || currentNavigation.value?.label || "审计控制台"
))
const sectionIndex = computed(() => (
  isReportRoute.value
    ? "REPORT"
    : route.meta.section || currentNavigation.value?.index || "00"
))
const auditAiExpiresText = computed(() => {
  const seconds = Math.max(0, Number(auditAiExpiresInSeconds.value) || 0)
  if (seconds >= 86400) return `${Math.floor(seconds / 86400)} 天 ${Math.floor((seconds % 86400) / 3600)} 小时`
  if (seconds >= 3600) return `${Math.floor(seconds / 3600)} 小时 ${Math.floor((seconds % 3600) / 60)} 分钟`
  return `${Math.max(1, Math.ceil(seconds / 60))} 分钟`
})

function saveKey() {
  storageError.value = ""
  const result = backendApiKey.value.trim()
    ? writeStorage("backendApiKey", backendApiKey.value)
    : removeStorage("backendApiKey")
  if (!result.ok) {
    storageError.value = "无法访问浏览器本地存储，设置未保存。"
  }
}

function clearKey() {
  backendApiKey.value = ""
  storageError.value = ""
}

async function openSettings(focus = "") {
  storageError.value = ""
  settingsFocus.value = focus
  const result = readStorage("backendApiKey")
  backendApiKey.value = result.value || ""
  if (!result.ok) {
    storageError.value = "无法访问浏览器本地存储，设置不会保存。"
  }
  settingsOpen.value = true
  await loadAuditAiConfig()
}

function discardSettings() {
  backendApiKey.value = ""
  storageError.value = ""
  settingsFocus.value = ""
  settingsPrompt.value = ""
  auditAiError.value = ""
  auditAi.apiKey = ""
}

function closeSettings() {
  settingsOpen.value = false
  discardSettings()
}

function applyProviderPreset(providerName) {
  const preset = auditAiProviders.find((provider) => provider.name === providerName)
  if (!preset) return
  auditAi.apiUrl = preset.apiUrl
  auditAi.model = preset.model
}

function setTtlDraft(ttlMinutes) {
  const minutes = Math.max(1, Number(ttlMinutes) || 1440)
  if (minutes % 1440 === 0) {
    auditAi.ttlValue = minutes / 1440
    auditAi.ttlUnit = "day"
  } else if (minutes % 60 === 0) {
    auditAi.ttlValue = minutes / 60
    auditAi.ttlUnit = "hour"
  } else {
    auditAi.ttlValue = minutes
    auditAi.ttlUnit = "minute"
  }
}

function ttlMinutesFromDraft() {
  const multiplier = auditAi.ttlUnit === "day" ? 1440 : auditAi.ttlUnit === "hour" ? 60 : 1
  return Math.round((Number(auditAi.ttlValue) || 0) * multiplier)
}

async function loadAuditAiConfig() {
  auditAiError.value = ""
  try {
    const config = await getAuditAiConfig()
    auditAiConfigured.value = Boolean(config?.configured)
    auditAiMasked.value = config?.apiKeyMasked || ""
    auditAiExpiresInSeconds.value = config?.expiresInSeconds || 0
    if (config?.configured) {
      auditAi.provider = config.provider || "自定义兼容接口"
      auditAi.apiUrl = config.apiUrl || ""
      auditAi.model = config.model || ""
      setTtlDraft(config.ttlMinutes)
    }
    auditAi.apiKey = ""
  } catch (error) {
    auditAiConfigured.value = false
    auditAiError.value = error?.response?.data?.error || error?.message || "无法读取审计 AI 配置"
  }
}

async function persistAuditAiConfig() {
  auditAiError.value = ""
  if (!auditAi.provider.trim() || !auditAi.apiUrl.trim() || !auditAi.model.trim()) {
    auditAiError.value = "请填写服务商、API URL 和模型。"
    return
  }
  if (!auditAiConfigured.value && !auditAi.apiKey.trim()) {
    auditAiError.value = "请配置审计 API Key"
    return
  }
  const ttlMinutes = ttlMinutesFromDraft()
  if (ttlMinutes < 1 || ttlMinutes > 43200) {
    auditAiError.value = "有效期需在 1 分钟至 30 天之间。"
    return
  }
  auditAiSaving.value = true
  try {
    const config = await saveAuditAiConfig({
      provider: auditAi.provider.trim(),
      apiUrl: auditAi.apiUrl.trim(),
      model: auditAi.model.trim(),
      apiKey: auditAi.apiKey.trim(),
      ttlMinutes
    })
    auditAiConfigured.value = true
    auditAiMasked.value = config.apiKeyMasked || ""
    auditAiExpiresInSeconds.value = config.expiresInSeconds || ttlMinutes * 60
    auditAi.apiKey = ""
    settingsPrompt.value = ""
    ElMessage.success("审计 AI 配置已保存，过期时间已重置")
  } catch (error) {
    auditAiError.value = error?.response?.data?.error || error?.message || "保存失败"
  } finally {
    auditAiSaving.value = false
  }
}

async function removeAuditAiConfig() {
  auditAiSaving.value = true
  auditAiError.value = ""
  try {
    await deleteAuditAiConfig()
    auditAiConfigured.value = false
    auditAiMasked.value = ""
    auditAiExpiresInSeconds.value = 0
    auditAi.apiKey = ""
    ElMessage.success("审计 AI 配置已删除")
  } catch (error) {
    auditAiError.value = error?.response?.data?.error || error?.message || "删除失败"
  } finally {
    auditAiSaving.value = false
  }
}

function openAuditAiSettings(message = "") {
  settingsPrompt.value = message
  openSettings("audit-ai")
}

provide("openAuditAiSettings", openAuditAiSettings)

watch(
  () => route.fullPath,
  (path) => {
    const match = /^\/report\/(\d+)/.exec(path)
    if (match) markAuditReportRead(Number(match[1]))
    if (path === "/history") markAllAuditReportsRead()
    syncUnreadAuditCount()
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener(AUDIT_READ_STATE_EVENT, syncUnreadAuditCount)
  pollAuditCompletions()
  auditCompletionTimer = window.setInterval(pollAuditCompletions, 5000)
})

onBeforeUnmount(() => {
  window.removeEventListener(AUDIT_READ_STATE_EVENT, syncUnreadAuditCount)
  if (auditCompletionTimer !== null) window.clearInterval(auditCompletionTimer)
})
</script>

<style scoped>
.console-shell {
  min-height: 100vh;
}

.console-sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 20;
  display: flex;
  width: 224px;
  flex-direction: column;
  box-sizing: border-box;
  padding: 22px 14px 16px;
  overflow-y: auto;
  background: var(--ta-sidebar);
  border-right: 1px solid var(--ta-line);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0 8px 20px;
  color: inherit;
  border-bottom: 1px solid var(--ta-line);
  text-decoration: none;
  transition: border-color 180ms ease;
}

.brand-block:hover {
  color: inherit;
  border-bottom-color: rgba(67, 224, 162, 0.3);
}

.brand-copy {
  min-width: 0;
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  flex: 0 0 auto;
  background: rgba(67, 224, 162, 0.06);
  border: 1px solid var(--ta-line-strong);
  border-radius: 5px;
  transition:
    color 180ms ease,
    background 180ms ease,
    border-color 180ms ease,
    transform 180ms ease;
}

.brand-mark img { display: block; width: 23px; height: 23px; }

.brand-block:hover .brand-mark,
.brand-block:focus-visible .brand-mark {
  background: var(--ta-green);
  border-color: var(--ta-green);
  transform: translateY(-1px);
}

.brand-block:hover .brand-mark img,
.brand-block:focus-visible .brand-mark img { filter: brightness(.18) saturate(.8); }

.brand-name {
  color: var(--ta-text);
  font-size: 15px;
  font-weight: 680;
  letter-spacing: 0.015em;
}

.brand-meta {
  margin-top: 4px;
  color: var(--ta-faint);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.brand-arrow {
  margin-left: auto;
  color: var(--ta-decorative);
  font-family: var(--ta-mono);
  font-size: 12px;
  transform: translate(-2px, 2px);
  transition:
    color 180ms ease,
    transform 180ms ease;
}

.brand-block:hover .brand-arrow,
.brand-block:focus-visible .brand-arrow {
  color: var(--ta-green);
  transform: translate(0, 0);
}

.nav-unread-dot {
  width: 7px;
  height: 7px;
  margin-left: auto;
  flex: 0 0 auto;
  background: var(--ta-danger);
  border-radius: 50%;
  box-shadow: 0 0 9px rgba(255, 102, 112, 0.62);
  animation: unread-pulse 1.8s ease-in-out infinite;
}

.mobile-unread-dot {
  width: 5px;
  height: 5px;
  background: var(--ta-danger);
  border-radius: 50%;
}

@keyframes unread-pulse {
  0%, 100% { opacity: .7; transform: scale(.9); }
  50% { opacity: 1; transform: scale(1.15); }
}

.system-state,
.environment-state {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--ta-muted);
  font-size: 11px;
}

.system-state {
  margin: 16px 8px 22px;
}

.state-indicator {
  width: 6px;
  height: 6px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--ta-green);
  box-shadow: 0 0 0 3px rgba(67, 224, 162, 0.08);
}

.state-code {
  margin-left: auto;
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  letter-spacing: 0.06em;
}

.primary-nav {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 4px;
}

.nav-label {
  padding: 0 10px 8px;
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
}

.nav-item {
  display: flex;
  min-height: 40px;
  align-items: center;
  gap: 11px;
  box-sizing: border-box;
  padding: 0 10px;
  color: var(--ta-muted);
  border: 1px solid transparent;
  border-radius: 5px;
  font-size: 13px;
  text-decoration: none;
}

.nav-item:hover {
  color: var(--ta-text);
  background: rgba(67, 224, 162, 0.035);
  border-color: var(--ta-line);
}

.nav-item.is-active {
  color: var(--ta-text);
  background: rgba(67, 224, 162, 0.07);
  border-color: var(--ta-line-strong);
}

.nav-item.is-active::after {
  width: 3px;
  height: 14px;
  margin-left: auto;
  content: "";
  background: var(--ta-green);
  border-radius: 1px;
}

.nav-index {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 10px;
}

.nav-item.is-active .nav-index {
  color: var(--ta-green);
}

.sidebar-foot {
  display: flex;
  justify-content: space-between;
  padding: 14px 8px 0;
  color: var(--ta-faint);
  border-top: 1px solid var(--ta-line);
  font-size: 10px;
}

.mono {
  font-family: var(--ta-mono);
}

.console-workspace {
  min-height: 100vh;
  margin-left: 224px;
}

.console-header {
  position: sticky;
  top: 0;
  z-index: 15;
  display: flex;
  min-height: 66px;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  padding: 10px 24px;
  background: var(--ta-bg);
  border-bottom: 1px solid var(--ta-line);
}

.header-eyebrow,
.settings-kicker {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 9px;
  letter-spacing: 0.14em;
}

.header-heading h1 {
  margin: 4px 0 0;
  color: var(--ta-text);
  font-size: 16px;
  font-weight: 620;
  letter-spacing: 0.025em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.environment-state {
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid var(--ta-line);
  border-radius: 4px;
}

.environment-state .mono {
  color: var(--ta-green);
  font-size: 10px;
  letter-spacing: 0.08em;
}

.settings-button {
  min-width: 58px;
}

.mobile-nav {
  display: none;
}

.console-main {
  min-height: calc(100vh - 66px);
  box-sizing: border-box;
  padding: 22px 24px 40px;
  background-image:
    linear-gradient(rgba(67, 224, 162, 0.018) 1px, transparent 1px),
    linear-gradient(90deg, rgba(67, 224, 162, 0.018) 1px, transparent 1px);
  background-size: 28px 28px;
}

.main-frame {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
}

.settings-wrap {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.012);
  border: 1px solid var(--ta-line);
  border-radius: 6px;
  transition: border-color 180ms ease, box-shadow 180ms ease;
}

.settings-section.is-focused {
  border-color: rgba(67, 224, 162, 0.42);
  box-shadow: 0 0 0 1px rgba(67, 224, 162, 0.08), 0 18px 50px rgba(0, 0, 0, 0.18);
}

.settings-section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.settings-status {
  display: inline-flex;
  min-height: 24px;
  align-items: center;
  padding: 0 8px;
  color: var(--ta-faint);
  background: var(--ta-code);
  border: 1px solid var(--ta-line);
  border-radius: 999px;
  font-family: var(--ta-mono);
  font-size: 10px;
  white-space: nowrap;
}

.settings-status.is-ready {
  color: var(--ta-green);
  background: rgba(67, 224, 162, 0.07);
  border-color: rgba(67, 224, 162, 0.26);
}

.settings-status.is-empty {
  color: #dfb777;
  border-color: rgba(223, 183, 119, 0.2);
}

.settings-status.is-local {
  color: var(--ta-muted);
}

.settings-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 138px;
  gap: 12px;
}

.settings-field {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 7px;
}

.settings-field.full {
  grid-column: 1 / -1;
}

.settings-field .el-select,
.settings-field .el-input-number {
  width: 100%;
}

.field-hint {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 10px;
}

.settings-prompt {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 12px;
  color: #c8f7df;
  background: rgba(67, 224, 162, 0.07);
  border: 1px solid rgba(67, 224, 162, 0.22);
  border-radius: var(--ta-radius);
  font-size: 12px;
  line-height: 1.5;
}

.settings-title {
  margin-top: 6px;
  color: var(--ta-text);
  font-size: 16px;
  font-weight: 650;
}

.settings-subtitle {
  margin: 8px 0 0;
  color: var(--ta-muted);
  font-size: 12px;
  line-height: 1.7;
}

.settings-field-label {
  color: var(--ta-muted);
  font-family: var(--ta-mono);
  font-size: 11px;
  letter-spacing: 0.04em;
}

.settings-note {
  padding: 10px 12px;
  color: var(--ta-faint);
  background: var(--ta-code);
  border: 1px solid var(--ta-line);
  border-radius: var(--ta-radius);
  font-size: 11px;
  line-height: 1.6;
}

.settings-error {
  margin: 0;
  padding: 10px 12px;
  color: #ffaaa7;
  background: rgba(255, 125, 121, 0.07);
  border: 1px solid rgba(255, 125, 121, 0.2);
  border-radius: var(--ta-radius);
  font-size: 12px;
  line-height: 1.6;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.settings-actions.compact {
  margin-top: 0;
}

.drawer-actions {
  padding-top: 2px;
  border-top: 1px solid var(--ta-line);
}

@media (max-width: 840px) {
  .console-sidebar {
    display: none;
  }

  .console-workspace {
    margin-left: 0;
  }

  .console-header {
    min-height: 60px;
    padding: 8px 14px;
  }

  .environment-label {
    display: none;
  }

  .environment-state {
    padding: 0 8px;
  }

  .mobile-nav {
    position: sticky;
    top: 60px;
    z-index: 14;
    display: flex;
    overflow-x: auto;
    padding: 8px 10px;
    background: var(--ta-sidebar);
    border-bottom: 1px solid var(--ta-line);
    scrollbar-width: none;
  }

  .mobile-nav::-webkit-scrollbar {
    display: none;
  }

  .mobile-nav-item {
    display: flex;
    min-width: max-content;
    min-height: 34px;
    align-items: center;
    gap: 6px;
    padding: 0 10px;
    color: var(--ta-muted);
    border: 1px solid transparent;
    border-radius: 4px;
    font-size: 12px;
    text-decoration: none;
  }

  .mobile-nav-item span:first-child {
    color: var(--ta-faint);
    font-family: var(--ta-mono);
    font-size: 9px;
  }

  .mobile-nav-item.is-active {
    color: var(--ta-text);
    background: rgba(67, 224, 162, 0.07);
    border-color: var(--ta-line-strong);
  }

  .mobile-nav-item.is-active span:first-child {
    color: var(--ta-green);
  }

  .console-main {
    min-height: calc(100vh - 111px);
    padding: 14px 12px 28px;
  }
}

@media (max-width: 520px) {
  .settings-section {
    padding: 14px;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .settings-field.full {
    grid-column: auto;
  }
}

@media (max-width: 520px) {
  .mobile-nav {
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 12px, #000 calc(100% - 22px), transparent);
    mask-image: linear-gradient(90deg, transparent, #000 12px, #000 calc(100% - 22px), transparent);
  }

  .header-eyebrow {
    display: none;
  }

  .header-heading h1 {
    margin-top: 0;
    font-size: 14px;
  }

  .header-actions {
    gap: 7px;
  }

  .settings-actions {
    flex-wrap: wrap;
  }
}
</style>
