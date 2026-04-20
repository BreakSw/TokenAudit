<template>
  <div class="app-bg" />
  <el-container class="app-shell">
    <el-header class="app-header">
      <div class="header-left">
        <div class="brand">
          <div class="brand-mark">
            <img src="/favicon.svg" alt="TokenAudit" />
          </div>
          <div class="brand-text">
            <div class="brand-title gradient-text">TokenAudit</div>
            <div class="brand-subtitle">多Agent · DeepSeek判定 · 证据可回溯</div>
          </div>
        </div>
      </div>
      <div class="header-right">
        <div class="header-pill">Local</div>
        <el-button size="small" type="primary" plain @click="openSettings">设置</el-button>
      </div>
    </el-header>
    <el-container class="app-body">
      <el-aside class="app-aside" width="240px">
        <div class="aside-card">
          <div class="aside-title">导航</div>
          <el-menu router :default-active="$route.path" class="aside-menu">
            <el-menu-item index="/">审计入口</el-menu-item>
            <el-menu-item index="/audit">发起审计</el-menu-item>
            <el-menu-item index="/tokens">Token管理</el-menu-item>
            <el-menu-item index="/history">历史记录</el-menu-item>
          </el-menu>
        </div>
      </el-aside>
      <el-main class="app-main">
        <div class="main-wrap">
          <router-view />
        </div>
      </el-main>
    </el-container>

    <el-drawer v-model="settingsOpen" size="420px" title="设置" :with-header="true">
      <div class="settings-wrap">
        <div class="settings-title">后端访问</div>
        <div class="settings-subtitle">如果后端开启了 X-API-KEY 校验，在这里填写即可（会保存在浏览器本地）。</div>
        <el-input
          v-model="backendApiKey"
          placeholder="后端 X-API-KEY（可选）"
          size="large"
          clearable
          @change="saveKey"
        />
        <div class="settings-actions">
          <el-button size="large" @click="settingsOpen = false">关闭</el-button>
          <el-button size="large" type="primary" @click="saveKey">保存</el-button>
        </div>
      </div>
    </el-drawer>
  </el-container>
</template>

<script setup>
import { ref } from "vue"

const backendApiKey = ref(localStorage.getItem("backendApiKey") || "")
const settingsOpen = ref(false)

function saveKey() {
  localStorage.setItem("backendApiKey", backendApiKey.value || "")
}

function openSettings() {
  settingsOpen.value = true
}
</script>

<style>
html,
body,
#app {
  height: 100%;
}

body {
  margin: 0;
  color: #111827;
}

.app-bg {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(1000px 700px at 10% 0%, rgba(37, 99, 235, 0.12), transparent 55%),
    radial-gradient(900px 700px at 90% 10%, rgba(16, 185, 129, 0.10), transparent 55%),
    linear-gradient(180deg, #f7f9ff 0%, #eef2ff 35%, #f3f4f6 100%);
  z-index: -1;
}

.app-shell {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 20px;
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid rgba(17, 24, 39, 0.08);
  box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
  backdrop-filter: blur(8px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(37, 99, 235, 0.18);
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.12);
}

.brand-mark img {
  width: 100%;
  height: 100%;
  display: block;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-weight: 800;
  letter-spacing: 0.2px;
  color: #0f172a;
  line-height: 18px;
}

.brand-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.62);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-pill {
  height: 30px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  color: rgba(15, 23, 42, 0.72);
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.app-body {
  padding: 18px;
}

.app-aside {
  padding-right: 16px;
}

.aside-card {
  padding: 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(17, 24, 39, 0.08);
  box-shadow: 0 18px 50px rgba(17, 24, 39, 0.08);
}

.aside-title {
  font-size: 12px;
  font-weight: 700;
  color: rgba(15, 23, 42, 0.7);
  margin-bottom: 8px;
  letter-spacing: 0.2px;
}

.aside-menu {
  border-right: none;
  background: transparent;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: rgba(37, 99, 235, 0.08);
  --el-menu-text-color: rgba(15, 23, 42, 0.78);
  --el-menu-active-color: rgb(37, 99, 235);
}

.aside-menu .el-menu-item {
  margin: 4px 6px;
  border-radius: 12px;
  height: 42px;
  line-height: 42px;
}

.aside-menu .el-menu-item:hover {
  color: rgba(15, 23, 42, 0.92);
}

.aside-menu .el-menu-item.is-active {
  background: rgba(37, 99, 235, 0.12);
  color: rgb(37, 99, 235);
  font-weight: 800;
  border: 1px solid rgba(37, 99, 235, 0.18);
  box-shadow: 0 12px 30px rgba(37, 99, 235, 0.12);
}

.app-main {
  padding: 0;
}

.main-wrap {
  max-width: 1180px;
  margin: 0 auto;
}

.settings-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.settings-title {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
}

.settings-subtitle {
  font-size: 12px;
  color: rgba(15, 23, 42, 0.62);
  margin-bottom: 6px;
}

.settings-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
}

.el-card {
  border-radius: 14px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 50px rgba(17, 24, 39, 0.08);
}

.el-card__header {
  border-bottom: 1px solid rgba(17, 24, 39, 0.08);
}

.el-table {
  border-radius: 12px;
}

@media (max-width: 920px) {
  .app-aside {
    display: none;
  }
}
</style>
