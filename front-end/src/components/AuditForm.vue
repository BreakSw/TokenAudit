<template>
  <div class="audit-console">
    <section
      v-reveal
      class="audit-heading"
      data-testid="audit-major-section"
      aria-labelledby="audit-workflow-title"
    >
      <div data-testid="audit-heading">
        <div class="eyebrow"><span class="signal-dot" />LIVE AUDIT / 实时取证</div>
        <h1 id="audit-workflow-title">实时审计工作流</h1>
        <p>面向 Token 的六个审计维度 + 综合判定，过程证据持续写入事件终端。</p>
      </div>
      <div class="heading-actions" aria-label="审计快捷入口">
        <el-button @click="router.push('/history')">历史审计</el-button>
        <el-button type="primary" plain @click="router.push('/tokens')">管理 Token</el-button>
      </div>
    </section>

    <section
      v-reveal="{ stagger: 45 }"
      class="console-panel configuration-panel"
      data-testid="audit-major-section"
      aria-labelledby="configuration-title"
    >
      <header class="panel-header" data-testid="audit-configuration">
        <div>
          <span class="panel-index">01 / CONFIG</span>
          <h2 id="configuration-title">Token 与导出配置</h2>
        </div>
        <span class="panel-note">选择审计对象与交付格式</span>
      </header>

      <div class="configuration-grid">
        <div class="field-block token-field">
          <label class="field-label" for="audit-token-select">审计 Token</label>
          <el-select
            id="audit-token-select"
            v-model="tokenId"
            :disabled="!tokens.length"
            filterable
            placeholder="选择一个可用 Token"
          >
            <el-option
              v-for="token in tokens"
              :key="token.id"
              :label="`${token.name} (${token.tokenMasked})`"
              :value="token.id"
            />
          </el-select>
          <p v-if="tokens.length" class="field-help">已载入 {{ tokens.length }} 个 Token，密钥仅显示脱敏标识。</p>
          <p v-else class="field-help field-help--warning" role="status">
            暂无可用 Token。请先前往“管理 Token”录入凭据，再刷新列表。
          </p>
        </div>

        <fieldset class="field-block format-field">
          <legend class="field-label">报告导出格式</legend>
          <el-checkbox-group v-model="exportFormats" class="format-options">
            <el-checkbox value="json">JSON</el-checkbox>
            <el-checkbox value="md">Markdown</el-checkbox>
            <el-checkbox value="xlsx">Excel</el-checkbox>
            <el-checkbox value="pdf">PDF</el-checkbox>
          </el-checkbox-group>
          <p class="field-help">PDF 需服务端配置中文字体，未配置时会自动跳过。</p>
        </fieldset>
      </div>

      <div class="configuration-actions">
        <el-button
          type="primary"
          :loading="submitting"
          :disabled="status === 'running'"
          @click="submit"
        >
          开始审计
        </el-button>
        <el-button :loading="loadingTokens" @click="reloadTokens">刷新 Token</el-button>
        <el-button @click="router.push('/tokens')">管理 Token</el-button>
        <el-button @click="router.push('/history')">历史</el-button>
        <el-button v-if="auditId" type="primary" plain @click="router.push(`/report/${auditId}`)">
          查看报告
        </el-button>
      </div>
    </section>

    <section
      v-reveal="{ stagger: 90 }"
      class="console-panel pipeline-panel"
      :class="`pipeline-panel--${status || 'ready'}`"
      data-testid="audit-major-section"
      aria-labelledby="pipeline-title"
    >
      <header class="panel-header" data-testid="audit-pipeline">
        <div>
          <span class="panel-index">02 / PIPELINE</span>
          <h2 id="pipeline-title">七阶段审计管线</h2>
        </div>
        <div class="pipeline-controls">
          <span class="status-chip" :class="`status-chip--${status || 'ready'}`">{{ statusText }}</span>
          <el-button size="small" :loading="refreshing" :disabled="!auditId" @click="refreshOnce">
            刷新进度
          </el-button>
        </div>
      </header>

      <div class="progress-overview">
        <div class="progress-copy">
          <strong>{{ auditId ? `${progress}%` : '0%' }}</strong>
          <span>{{ auditId ? currentStageLabel : "等待启动" }}</span>
        </div>
        <el-progress :percentage="auditId ? progress : 0" :stroke-width="6" :show-text="false" />
        <dl class="progress-meta">
          <div>
            <dt>审计 ID</dt>
            <dd>{{ auditId || "—" }}</dd>
          </div>
          <div>
            <dt>当前阶段</dt>
            <dd>{{ auditId ? currentStageLabel : "准备态" }}</dd>
          </div>
          <div>
            <dt>状态</dt>
            <dd>{{ statusText }}</dd>
          </div>
        </dl>
        <p class="progress-hint">
          {{ progressHint || "选择 Token 并开始审计后，七阶段证据将在此实时推进。" }}
        </p>
      </div>

      <ol class="stage-list" aria-label="审计阶段">
        <li
          v-for="(stage, index) in AUDIT_STAGES"
          :key="stage.key"
          class="audit-stage"
          :class="`audit-stage--${stageState(index)}`"
          data-testid="audit-stage"
        >
          <span class="stage-marker">{{ String(index + 1).padStart(2, "0") }}</span>
          <div class="stage-copy">
            <strong>{{ stage.label }}</strong>
            <span>{{ stage.detail }}</span>
          </div>
          <span class="stage-state">{{ stageStateText(index) }}</span>
        </li>
      </ol>
    </section>

    <section
      v-reveal="{ stagger: 135 }"
      class="console-panel terminal-panel"
      data-testid="audit-major-section"
      aria-labelledby="terminal-title"
    >
      <header class="panel-header terminal-header" data-testid="audit-terminal">
        <div>
          <span class="panel-index">03 / EVENT STREAM</span>
          <h2 id="terminal-title">实时事件终端</h2>
        </div>
        <div class="terminal-actions">
          <span>{{ displayEvents.length }} / 200 EVENTS</span>
          <el-button size="small" :disabled="!displayEvents.length" @click="clearView">清空显示</el-button>
        </div>
      </header>

      <div class="terminal-window" role="log" aria-live="polite" aria-label="审计实时事件">
        <div v-if="!displayEvents.length" class="terminal-empty">
          <span class="terminal-prompt">$</span>
          <div>
            <strong>暂无审计事件</strong>
            <p>{{ auditId ? "等待后端返回下一条审计证据…" : "启动审计后，调用状态与耗时将在这里逐行显示。" }}</p>
          </div>
        </div>

        <article
          v-for="(row, index) in displayEvents"
          v-else
          :key="`${row.ts || 'event'}-${index}`"
          class="terminal-event"
          data-testid="terminal-event"
        >
          <div class="event-lead">
            <time data-testid="event-timestamp">{{ row.ts || "—" }}</time>
            <el-tag data-testid="event-tag" size="small" :type="eventTagType(row.event)">
              {{ row.event || "unknown_event" }}
            </el-tag>
          </div>
          <p class="event-explanation" data-testid="event-explanation">{{ eventText(row) }}</p>
          <dl v-if="eventDetails(row).length" class="event-details">
            <div v-for="detail in eventDetails(row)" :key="detail.key">
              <dt>{{ detail.label }}</dt>
              <dd>{{ detail.value }}</dd>
            </div>
          </dl>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { getAudit, listAuditEvents, listTokens, startAudit } from "../request/api"
import { AUDIT_STAGES, stageIndex, stageLabel } from "../constants/auditStages"
import { readStorage, removeStorage, writeStorage } from "../utils/storage"

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
let pollTimer = null
const LAST_AUDIT_ID_KEY = "lastAuditId"

const displayEvents = computed(() => events.value.slice(-200))

const currentStage = computed(() => {
  const validPhases = new Set(AUDIT_STAGES.map((stage) => stage.key))
  for (let i = events.value.length - 1; i >= 0; i -= 1) {
    const e = events.value[i]
    const phase = e?.payload?.phase
    if (e?.event === "phase_start" && validPhases.has(phase)) return phase
    if (e?.event === "deepseek_call_start" && phase === "overall") return "overall"
  }
  return ""
})

const activeStepIndex = computed(() => stageIndex(currentStage.value))

const currentStageLabel = computed(() => stageLabel(currentStage.value))

const statusText = computed(() => {
  if (status.value === "running") return "审计中"
  if (status.value === "completed") return "已完成"
  if (status.value === "failed") return "失败"
  return status.value || "准备就绪"
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

function stageState(index) {
  if (!auditId.value) return "ready"
  if (status.value === "completed") return "completed"
  if (index < activeStepIndex.value) return "completed"
  if (currentStage.value && index === activeStepIndex.value) {
    return status.value === "failed" ? "failed" : "running"
  }
  return "pending"
}

function stageStateText(index) {
  const labels = {
    ready: "待命",
    pending: "等待",
    running: "执行中",
    completed: "完成",
    failed: "中断"
  }
  return labels[stageState(index)]
}

function eventDetails(row) {
  const payload = row?.payload || {}
  const details = []
  if (payload.status_code !== undefined && payload.status_code !== null) {
    details.push({ key: "status_code", label: "STATUS", value: `HTTP ${payload.status_code}` })
  }
  if (payload.elapsed_ms !== undefined && payload.elapsed_ms !== null) {
    details.push({ key: "elapsed_ms", label: "LATENCY", value: `${payload.elapsed_ms} ms` })
  }
  if (payload.model) details.push({ key: "model", label: "MODEL", value: payload.model })
  if (payload.phase) {
    const phaseName = stageLabel(payload.phase)
    details.push({ key: "phase", label: "PHASE", value: phaseName === "-" ? payload.phase : phaseName })
  }
  if (payload.scenario) details.push({ key: "scenario", label: "SCENARIO", value: payload.scenario })
  if (payload.status) details.push({ key: "status", label: "RESULT", value: payload.status })
  return details
}

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
  const { value: v } = readStorage(LAST_AUDIT_ID_KEY)
  if (!v) return null
  const n = Number(v)
  if (!Number.isFinite(n) || n <= 0) return null
  return n
}

function saveLastAuditId(id) {
  writeStorage(LAST_AUDIT_ID_KEY, String(id))
}

function clearLastAuditId() {
  removeStorage(LAST_AUDIT_ID_KEY)
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
.audit-console {
  display: grid;
  gap: 14px;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
}

.audit-heading,
.panel-header,
.configuration-actions,
.pipeline-controls,
.terminal-actions,
.event-lead {
  display: flex;
  align-items: center;
}

.audit-heading {
  justify-content: space-between;
  gap: 24px;
  padding: 6px 0 10px;
  border-bottom: 1px solid var(--ta-line);
}

.eyebrow,
.panel-index,
.panel-note,
.field-label,
.terminal-actions,
.event-lead,
.event-details,
.progress-meta,
.stage-state {
  font-family: var(--ta-mono);
}

.eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--ta-green);
  font-size: 11px;
  letter-spacing: 0.08em;
}

.signal-dot {
  width: 6px;
  height: 6px;
  background: var(--ta-green);
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(67, 224, 162, 0.58);
}

.audit-heading h1 {
  margin: 5px 0 2px;
  color: var(--ta-text);
  font-size: clamp(24px, 3vw, 34px);
  font-weight: 650;
  letter-spacing: -0.035em;
}

.audit-heading p {
  margin: 0;
  color: var(--ta-muted);
  font-size: 13px;
}

.heading-actions,
.configuration-actions,
.pipeline-controls,
.terminal-actions {
  gap: 8px;
  flex-wrap: wrap;
}

.heading-actions {
  justify-content: flex-end;
}

.console-panel {
  overflow: hidden;
  background: var(--ta-panel);
  border: 1px solid var(--ta-line);
  border-radius: var(--ta-radius);
}

.panel-header {
  justify-content: space-between;
  gap: 18px;
  min-height: 58px;
  padding: 11px 14px;
  background: var(--ta-panel-raised);
  border-bottom: 1px solid var(--ta-line);
}

.panel-index {
  display: block;
  margin-bottom: 2px;
  color: var(--ta-green);
  font-size: 10px;
  letter-spacing: 0.1em;
}

.panel-header h2 {
  margin: 0;
  color: var(--ta-text);
  font-size: 15px;
  font-weight: 650;
}

.panel-note,
.terminal-actions {
  color: var(--ta-faint);
  font-size: 11px;
}

.configuration-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1.1fr) minmax(320px, 1fr);
  gap: 0;
}

.field-block {
  min-width: 0;
  margin: 0;
  padding: 16px;
  border: 0;
}

.format-field {
  border-left: 1px solid var(--ta-line);
}

.field-label {
  display: block;
  margin-bottom: 8px;
  padding: 0;
  color: var(--ta-text);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.token-field :deep(.el-select) {
  width: 100%;
}

.field-help {
  min-height: 18px;
  margin: 7px 0 0;
  color: var(--ta-faint);
  font-size: 11px;
}

.field-help--warning {
  color: var(--ta-amber);
}

.format-options {
  display: flex;
  gap: 5px 18px;
  flex-wrap: wrap;
}

.format-options :deep(.el-checkbox) {
  margin-right: 0;
}

.configuration-actions {
  padding: 11px 14px;
  border-top: 1px solid var(--ta-line);
}

.pipeline-panel--running {
  border-color: rgba(233, 187, 99, 0.25);
}

.pipeline-panel--completed {
  border-color: rgba(67, 224, 162, 0.32);
}

.pipeline-panel--failed {
  border-color: rgba(255, 125, 121, 0.34);
}

.status-chip {
  padding: 3px 8px;
  color: var(--ta-faint);
  background: var(--ta-code);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
  font-family: var(--ta-mono);
  font-size: 10px;
  letter-spacing: 0.05em;
}

.status-chip--running {
  color: var(--ta-amber);
  border-color: rgba(233, 187, 99, 0.28);
}

.status-chip--completed {
  color: var(--ta-green);
  border-color: rgba(67, 224, 162, 0.32);
}

.status-chip--failed {
  color: var(--ta-danger);
  border-color: rgba(255, 125, 121, 0.32);
}

.progress-overview {
  padding: 15px 14px 13px;
  border-bottom: 1px solid var(--ta-line);
}

.progress-copy {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 9px;
}

.progress-copy strong {
  color: var(--ta-green);
  font-family: var(--ta-mono);
  font-size: 22px;
  font-weight: 600;
}

.progress-copy span {
  color: var(--ta-muted);
  font-size: 12px;
}

.progress-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  margin: 13px 0 0;
  background: var(--ta-line);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
}

.progress-meta div {
  min-width: 0;
  padding: 8px 10px;
  background: var(--ta-code);
}

.progress-meta dt {
  color: var(--ta-faint);
  font-size: 9px;
  letter-spacing: 0.08em;
}

.progress-meta dd {
  overflow-wrap: anywhere;
  margin: 2px 0 0;
  color: var(--ta-text);
  font-size: 11px;
}

.progress-hint {
  margin: 10px 0 0;
  color: var(--ta-muted);
  font-size: 11px;
}

.stage-list {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  margin: 0;
  padding: 0;
  list-style: none;
}

.audit-stage {
  position: relative;
  min-width: 0;
  min-height: 130px;
  padding: 14px 12px;
  background: var(--ta-panel);
  border-right: 1px solid var(--ta-line);
}

.audit-stage:last-child {
  border-right: 0;
}

.audit-stage::before {
  position: absolute;
  inset: 0 auto auto 0;
  width: 100%;
  height: 2px;
  background: transparent;
  content: "";
}

.audit-stage--running::before {
  background: var(--ta-amber);
}

.audit-stage--completed::before {
  background: var(--ta-green);
}

.audit-stage--failed::before {
  background: var(--ta-danger);
}

.stage-marker {
  display: inline-grid;
  width: 25px;
  height: 22px;
  place-items: center;
  color: var(--ta-faint);
  background: var(--ta-code);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
  font-family: var(--ta-mono);
  font-size: 10px;
}

.audit-stage--running .stage-marker {
  color: var(--ta-amber);
  border-color: rgba(233, 187, 99, 0.3);
}

.audit-stage--completed .stage-marker {
  color: var(--ta-green);
  border-color: rgba(67, 224, 162, 0.3);
}

.audit-stage--failed .stage-marker {
  color: var(--ta-danger);
  border-color: rgba(255, 125, 121, 0.3);
}

.stage-copy {
  display: grid;
  gap: 5px;
  margin-top: 10px;
}

.stage-copy strong {
  color: var(--ta-text);
  font-size: 12px;
  font-weight: 650;
}

.stage-copy span {
  color: var(--ta-faint);
  font-size: 10px;
  line-height: 1.45;
}

.stage-state {
  display: block;
  margin-top: 9px;
  color: var(--ta-decorative);
  font-size: 9px;
  letter-spacing: 0.05em;
}

.audit-stage--running .stage-state {
  color: var(--ta-amber);
}

.audit-stage--completed .stage-state {
  color: var(--ta-green);
}

.audit-stage--failed .stage-state {
  color: var(--ta-danger);
}

.terminal-panel {
  background: var(--ta-code);
}

.terminal-header {
  background: #07100b;
}

.terminal-window {
  max-height: 520px;
  overflow: auto;
  background:
    linear-gradient(rgba(67, 224, 162, 0.018) 1px, transparent 1px),
    var(--ta-code);
  background-size: 100% 28px;
  font-family: var(--ta-mono);
}

.terminal-empty {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  min-height: 150px;
  padding: 24px;
  color: var(--ta-muted);
}

.terminal-empty strong {
  color: var(--ta-text);
  font-size: 12px;
  font-weight: 500;
}

.terminal-empty p {
  margin: 5px 0 0;
  color: var(--ta-faint);
  font-size: 11px;
}

.terminal-prompt {
  color: var(--ta-green);
}

.terminal-event {
  display: grid;
  grid-template-columns: minmax(265px, 0.7fr) minmax(280px, 1.1fr) minmax(300px, 1fr);
  gap: 14px;
  align-items: start;
  min-width: 880px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--ta-line);
}

.terminal-event:hover {
  background: rgba(67, 224, 162, 0.025);
}

.event-lead {
  gap: 9px;
  min-width: 0;
}

.event-lead time {
  color: var(--ta-faint);
  font-size: 10px;
  white-space: nowrap;
}

.event-explanation {
  margin: 1px 0 0;
  color: var(--ta-text);
  font-size: 11px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.event-details {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin: 0;
}

.event-details div {
  display: flex;
  gap: 5px;
  min-width: 0;
  padding: 3px 6px;
  background: rgba(67, 224, 162, 0.035);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
}

.event-details dt {
  color: var(--ta-faint);
  font-size: 8px;
  letter-spacing: 0.06em;
}

.event-details dd {
  overflow-wrap: anywhere;
  margin: 0;
  color: var(--ta-green);
  font-size: 9px;
}

@media (max-width: 1100px) {
  .stage-list {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .audit-stage {
    border-bottom: 1px solid var(--ta-line);
  }

  .audit-stage:nth-child(4n) {
    border-right: 0;
  }

  .audit-stage:nth-last-child(-n + 3) {
    border-bottom: 0;
  }
}

@media (max-width: 840px) {
  .audit-heading {
    align-items: flex-start;
  }

  .configuration-grid {
    grid-template-columns: 1fr;
  }

  .format-field {
    border-top: 1px solid var(--ta-line);
    border-left: 0;
  }

  .stage-list {
    grid-template-columns: 1fr;
  }

  .audit-stage {
    display: grid;
    grid-template-columns: 32px minmax(0, 1fr) auto;
    gap: 9px;
    align-items: start;
    min-height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--ta-line) !important;
  }

  .audit-stage:last-child {
    border-bottom: 0 !important;
  }

  .stage-copy,
  .stage-state {
    margin-top: 0;
  }

  .terminal-event {
    grid-template-columns: 1fr;
    min-width: 0;
  }
}

@media (max-width: 600px) {
  .audit-console {
    gap: 10px;
  }

  .audit-heading,
  .panel-header {
    align-items: stretch;
    flex-direction: column;
  }

  .heading-actions,
  .configuration-actions,
  .pipeline-controls,
  .terminal-actions {
    justify-content: stretch;
  }

  .heading-actions :deep(.el-button),
  .configuration-actions :deep(.el-button) {
    flex: 1 1 calc(50% - 4px);
    margin-left: 0;
  }

  .progress-meta {
    grid-template-columns: 1fr;
  }

  .format-options {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
  }

  .terminal-actions {
    align-items: center;
    justify-content: space-between;
  }

  .event-lead {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
