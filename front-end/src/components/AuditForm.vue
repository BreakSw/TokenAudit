<template>
  <el-card class="audit-card">
    <template #header>
      <div class="card-header">
        <div>
          <div class="card-title">发起审计</div>
          <div class="card-subtitle">选择Token与导出格式，一键执行 5 项全维度审计</div>
        </div>
        <div class="card-actions">
          <el-button @click="reloadTokens" :loading="loadingTokens">刷新Token列表</el-button>
          <el-button type="primary" plain @click="$router.push('/tokens')">去管理Token</el-button>
        </div>
      </div>
    </template>

    <el-collapse v-model="openGuide" style="margin-bottom: 14px">
      <el-collapse-item name="guide" title="新手教程（建议先展开看一遍）">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-alert
              type="info"
              show-icon
              :closable="false"
              title="1) 先录入Token"
              description="进入「Token管理」新增一条Token记录。Base URL 只填域名根（例如 https://api.xiaoma.best），宣称模型填中转站返回的 model（例如 claude-opus-4-6）。"
            />
          </el-col>
          <el-col :span="12">
            <el-alert
              type="success"
              show-icon
              :closable="false"
              title="2) 发起审计"
              description="选择Token后点击「开始审计」。页面会显示真实进度与每一步的调用记录（token_call/deepseek_call）。"
            />
          </el-col>
        </el-row>
        <el-row :gutter="16" style="margin-top: 12px">
          <el-col :span="12">
            <el-alert
              type="warning"
              show-icon
              :closable="false"
              title="3) 导出格式怎么选"
              description="json/markdown/excel 为常用；pdf 需要配置字体（AUDIT_PDF_FONT_TTF），否则会自动跳过 PDF 导出。"
            />
          </el-col>
          <el-col :span="12">
            <el-alert
              type="info"
              show-icon
              :closable="false"
              title="4) 审计大概多久"
              description="一次审计包含约 25 次中转调用 + 6 次 DeepSeek 判定；通常 1–8 分钟，取决于平台速度与限流。"
            />
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>

    <el-row :gutter="16">
      <el-col :span="14">
        <el-form class="audit-form" label-width="120px">
          <el-form-item label="选择Token">
            <el-select v-model="tokenId" placeholder="请选择" filterable style="width: 100%">
              <el-option v-for="t in tokens" :key="t.id" :label="`${t.name} (${t.tokenMasked})`" :value="t.id" />
            </el-select>
          </el-form-item>

          <el-form-item label="导出格式">
            <el-checkbox-group v-model="exportFormats">
              <el-checkbox label="json" />
              <el-checkbox label="md" />
              <el-checkbox label="xlsx" />
              <el-checkbox label="pdf" />
            </el-checkbox-group>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="large" :loading="submitting" :disabled="status === 'running'" @click="submit">
              开始审计
            </el-button>
            <el-button size="large" @click="$router.push('/history')">查看历史</el-button>
            <el-button v-if="auditId" size="large" type="primary" plain @click="router.push(`/report/${auditId}`)">查看报告</el-button>
          </el-form-item>
        </el-form>

        <div class="progress-card">
          <div class="progress-head">
            <div class="progress-title">实时进度</div>
            <div style="display: flex; gap: 10px; align-items: center">
              <el-tag :type="statusTagType">{{ statusText }}</el-tag>
              <el-button size="small" @click="refreshOnce" :loading="refreshing" :disabled="!auditId">刷新</el-button>
            </div>
          </div>
          <el-progress :percentage="auditId ? progress : 0" :stroke-width="10" />
          <div class="stage-row">
            <el-tag v-if="auditId" size="small" type="info">当前阶段：{{ currentStageLabel }}</el-tag>
            <div v-else class="stage-placeholder">开始审计后，这里会显示实时进度与当前审计阶段</div>
          </div>
          <el-steps v-if="auditId" :active="activeStepIndex" align-center class="stage-steps">
            <el-step title="有效性" />
            <el-step title="权限" />
            <el-step title="掺水" />
            <el-step title="合规" />
            <el-step title="稳定" />
            <el-step title="综合判定" />
          </el-steps>
          <div class="progress-meta">
            <div>审计ID：{{ auditId || "-" }}</div>
            <div v-if="progressHint">{{ progressHint }}</div>
          </div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="right-pane">
          <div class="pane-title">执行内容</div>
          <el-steps direction="vertical" :active="sideActiveStep" class="pane-steps">
            <el-step title="有效性" description="3次不同指令调用，记录状态码/耗时/响应" />
            <el-step title="权限" description="宣称模型/非宣称模型/匿名调用三场景校验" />
            <el-step title="掺水" description="多轮响应特征提取与能力差异判定" />
            <el-step title="合规" description="泄露/匿名/高频调用风险检测" />
            <el-step title="稳定" description="同指令5次调用一致性与波动分析" />
          </el-steps>
          <el-alert
            style="margin-top: 12px"
            type="warning"
            show-icon
            :closable="false"
            title="注意"
            description="PDF导出需要配置字体（AUDIT_PDF_FONT_TTF），否则会自动跳过PDF导出。"
          />
        </div>
      </el-col>
    </el-row>

    <div v-if="auditId" style="margin-top: 14px">
      <el-card>
        <template #header>
          <div class="card-header">
            <div>
              <div class="card-title">审计过程（真实进度）</div>
              <div class="card-subtitle">这里展示后端实时采集到的每一步事件（来自 Python 多Agent stderr）</div>
            </div>
            <el-button size="small" @click="clearView">清空显示</el-button>
          </div>
        </template>

        <el-table :data="displayEvents" height="360" stripe style="width: 100%">
          <el-table-column prop="ts" label="时间" width="210" />
          <el-table-column prop="event" label="事件" width="160">
            <template #default="{ row }">
              <el-tag size="small" :type="eventTagType(row.event)">{{ row.event }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="说明">
            <template #default="{ row }">
              <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ eventText(row) }}</div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </el-card>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { getAudit, listAuditEvents, listTokens, startAudit } from "../request/api"

const router = useRouter()
const tokens = ref([])
const tokenId = ref(null)
const exportFormats = ref(["json", "md", "xlsx"])
const loadingTokens = ref(false)
const submitting = ref(false)

const auditId = ref(null)
const status = ref("")
const progress = ref(0)
const refreshing = ref(false)
const events = ref([])
const openGuide = ref(["guide"])
let pollTimer = null
const LAST_AUDIT_ID_KEY = "lastAuditId"

const displayEvents = computed(() => events.value.slice(-200))

const activeStepIndex = computed(() => {
  const p = currentStage.value
  if (p === "validity") return 0
  if (p === "permission") return 1
  if (p === "watering") return 2
  if (p === "compliance") return 3
  if (p === "stability") return 4
  if (p === "overall") return 5
  return 0
})

const sideActiveStep = computed(() => {
  const idx = activeStepIndex.value
  return Math.min(idx, 4)
})

const currentStage = computed(() => {
  const phaseOrder = new Set(["validity", "permission", "watering", "compliance", "stability", "overall"])
  for (let i = events.value.length - 1; i >= 0; i -= 1) {
    const e = events.value[i]
    const phase = e?.payload?.phase
    if (e?.event === "phase_start" && phaseOrder.has(phase)) return phase
    if (e?.event === "deepseek_call_start" && phase === "overall") return "overall"
  }
  return ""
})

const currentStageLabel = computed(() => {
  const p = currentStage.value
  if (p === "validity") return "有效性审计"
  if (p === "permission") return "权限审计"
  if (p === "watering") return "掺水审计"
  if (p === "compliance") return "合规性审计"
  if (p === "stability") return "稳定性审计"
  if (p === "overall") return "综合判定"
  return "-"
})

const statusText = computed(() => {
  if (status.value === "running") return "审计中"
  if (status.value === "completed") return "已完成"
  if (status.value === "failed") return "失败"
  return status.value || "-"
})
const statusTagType = computed(() => {
  if (status.value === "running") return "warning"
  if (status.value === "completed") return "success"
  if (status.value === "failed") return "danger"
  return "info"
})
const progressHint = computed(() => {
  if (status.value === "running" && progress.value >= 95) return "正在生成综合结论与报告内容..."
  if (status.value === "running") return "正在执行多Agent审计与 DeepSeek 判定..."
  if (status.value === "completed") return "审计已完成，可进入报告页查看详情"
  if (status.value === "failed") return "审计失败，可查看事件列表定位失败位置"
  return ""
})

async function reloadTokens() {
  loadingTokens.value = true
  try {
    tokens.value = await listTokens()
    if (!tokenId.value && tokens.value.length) {
      tokenId.value = tokens.value[0].id
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "加载失败")
  } finally {
    loadingTokens.value = false
  }
}

function loadLastAuditId() {
  const v = localStorage.getItem(LAST_AUDIT_ID_KEY)
  if (!v) return null
  const n = Number(v)
  if (!Number.isFinite(n) || n <= 0) return null
  return n
}

function saveLastAuditId(id) {
  localStorage.setItem(LAST_AUDIT_ID_KEY, String(id))
}

function clearLastAuditId() {
  localStorage.removeItem(LAST_AUDIT_ID_KEY)
}

function startPolling(id) {
  stopPolling()
  pollTimer = setInterval(() => {
    refreshOnce()
  }, 1200)
  refreshOnce()
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function refreshOnce() {
  if (!auditId.value) return
  refreshing.value = true
  try {
    const a = await getAudit(auditId.value)
    status.value = a.status
    progress.value = a.progress ?? 0
    const e = await listAuditEvents(auditId.value)
    events.value = e || []

    if (status.value === "completed") {
      progress.value = 100
      stopPolling()
      clearLastAuditId()
    }
    if (status.value === "failed") {
      progress.value = 100
      stopPolling()
      clearLastAuditId()
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "刷新失败")
  } finally {
    refreshing.value = false
  }
}

async function submit() {
  if (!tokenId.value) {
    ElMessage.warning("请先选择Token")
    return
  }
  submitting.value = true
  try {
    const res = await startAudit({ tokenId: tokenId.value, exportFormats: exportFormats.value })
    auditId.value = res.auditId
    saveLastAuditId(auditId.value)
    status.value = "running"
    progress.value = 0
    events.value = []
    ElMessage.success("已开始审计，正在实时更新进度")
    startPolling(auditId.value)
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "审计失败")
  } finally {
    submitting.value = false
  }
}

function clearView() {
  events.value = []
}

function eventTagType(ev) {
  if (ev === "token_call_end") return "info"
  if (ev === "deepseek_call_end") return "success"
  if (ev === "audit_failed") return "danger"
  if (ev === "audit_completed") return "success"
  if (ev === "phase_start") return "warning"
  return "default"
}

function eventText(row) {
  const ev = row.event
  const p = row.payload || {}
  if (ev === "phase_start") return `开始阶段：${p.phase || ""}`
  if (ev === "phase_end") return `结束阶段：${p.phase || ""}`
  if (ev === "token_call_start") return `调用中转模型：${p.model || ""} ${p.scenario ? `(${p.scenario})` : ""}`
  if (ev === "token_call_end") return `中转返回：status=${p.status_code} 耗时=${p.elapsed_ms}ms`
  if (ev === "deepseek_call_start") return `DeepSeek 判定：${p.model || ""}`
  if (ev === "deepseek_call_end") return `DeepSeek 返回：耗时=${p.elapsed_ms}ms`
  if (ev === "audit_start") return "开始审计任务"
  if (ev === "audit_completed") return `审计完成：${p.overallConclusion || ""}`
  if (ev === "audit_failed") return `审计失败：${p.error || ""}`
  return JSON.stringify(p)
}

onMounted(reloadTokens)
onMounted(async () => {
  const lastId = loadLastAuditId()
  if (!lastId) return
  auditId.value = lastId
  await refreshOnce()
  if (status.value === "running") {
    startPolling(auditId.value)
  }
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.card-title {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
  line-height: 18px;
}

.card-subtitle {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.62);
}

.card-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.audit-form {
  margin-top: 4px;
}

.right-pane {
  padding: 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.pane-title {
  font-weight: 800;
  color: rgba(15, 23, 42, 0.86);
  margin-bottom: 10px;
}

.pane-steps {
  padding-right: 10px;
}

.progress-card {
  margin-top: 12px;
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  gap: 10px;
}

.progress-title {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
}

.progress-meta {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  color: rgba(15, 23, 42, 0.62);
  font-size: 12px;
}

.stage-row {
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.stage-placeholder {
  color: rgba(15, 23, 42, 0.62);
  font-size: 12px;
}

.stage-steps {
  margin-top: 10px;
}
</style>
