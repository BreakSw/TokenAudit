<template>
  <div class="console-shell">
    <aside class="console-sidebar" aria-label="主导航">
      <div class="brand-block">
        <div class="brand-mark" aria-hidden="true">TA</div>
        <div>
          <div class="brand-name">TokenAudit</div>
          <div class="brand-meta">安全审计控制台</div>
        </div>
      </div>

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
        >
          <span class="nav-index">{{ item.index }}</span>
          <span>{{ item.label }}</span>
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
          <el-button class="settings-button" size="small" @click="openSettings">
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
        >
          <span>{{ item.index }}</span>
          <span>{{ item.shortLabel }}</span>
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
      size="420px"
      title="控制台设置"
      :with-header="true"
      @closed="discardSettings"
    >
      <div class="settings-wrap">
        <div>
          <div class="settings-kicker">API ACCESS</div>
          <div class="settings-title">后端访问密钥</div>
          <p class="settings-subtitle">
            若后端启用了 X-API-KEY 校验，请在此保存访问密钥。密钥仅存储在当前浏览器本地。
          </p>
        </div>

        <label class="settings-field-label" for="backend-api-key">X-API-KEY</label>
        <el-input
          id="backend-api-key"
          v-model="backendApiKey"
          placeholder="可选"
          size="large"
          clearable
          show-password
        />

        <p v-if="storageError" class="settings-error" role="alert" aria-live="assertive">
          {{ storageError }}
        </p>

        <div class="settings-note">
          请求发出时会从 <span class="mono">backendApiKey</span> 读取，并写入
          <span class="mono">X-API-KEY</span> 请求头。
        </div>

        <div class="settings-actions">
          <el-button size="large" @click="clearKey">清除</el-button>
          <el-button size="large" @click="closeSettings">关闭</el-button>
          <el-button size="large" type="primary" @click="saveKey">保存</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { readStorage, removeStorage, writeStorage } from "./utils/storage"

const navigation = [
  { path: "/", label: "审计控制台", shortLabel: "控制台", index: "00" },
  { path: "/audit", label: "发起审计", shortLabel: "审计", index: "01" },
  { path: "/tokens", label: "Token 管理", shortLabel: "Token", index: "02" },
  { path: "/history", label: "历史记录", shortLabel: "历史", index: "03" },
  { path: "/guide", label: "使用文档", shortLabel: "文档", index: "04" }
]

const route = useRoute()
const backendApiKey = ref("")
const settingsOpen = ref(false)
const storageError = ref("")

const isReportRoute = computed(() => route.path.startsWith("/report/"))
const activePath = computed(() => (isReportRoute.value ? "/history" : route.path))
const currentNavigation = computed(() => navigation.find((item) => item.path === activePath.value))
const currentTitle = computed(() => (isReportRoute.value ? "审计报告" : currentNavigation.value?.label || "审计控制台"))
const sectionIndex = computed(() => (isReportRoute.value ? "REPORT" : currentNavigation.value?.index || "00"))

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

function openSettings() {
  storageError.value = ""
  const result = readStorage("backendApiKey")
  backendApiKey.value = result.value || ""
  if (!result.ok) {
    storageError.value = "无法访问浏览器本地存储，设置不会保存。"
  }
  settingsOpen.value = true
}

function discardSettings() {
  backendApiKey.value = ""
  storageError.value = ""
}

function closeSettings() {
  settingsOpen.value = false
  discardSettings()
}
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
  border-bottom: 1px solid var(--ta-line);
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  flex: 0 0 auto;
  color: var(--ta-green);
  background: rgba(67, 224, 162, 0.06);
  border: 1px solid var(--ta-line-strong);
  border-radius: 5px;
  font-family: var(--ta-mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

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
