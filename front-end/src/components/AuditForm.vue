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
            :disabled="loadingTokens || !tokens.length"
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
          <p v-if="loadingTokens" class="field-help" role="status">正在加载 Token…</p>
          <p v-else-if="tokenError" class="field-help field-help--warning" role="alert">
            {{ tokenError }}
            <el-button data-testid="retry-tokens" link type="primary" @click="reloadTokens">重试</el-button>
          </p>
          <p v-else-if="tokens.length" class="field-help">已载入 {{ tokens.length }} 个 Token，密钥仅显示脱敏标识。</p>
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
          :disabled="!tokenId"
          @click="submit"
        >
          {{ status === "running" ? "并行新建审计" : "开始审计" }}
        </el-button>
        <el-button :loading="loadingTokens" @click="reloadTokens">刷新 Token</el-button>
        <el-button @click="router.push('/tokens')">管理 Token</el-button>
        <el-button @click="router.push('/history')">历史</el-button>
        <el-button v-if="auditId && status === 'completed'" type="primary" plain @click="router.push(`/report/${auditId}`)">
          查看报告
        </el-button>
        <el-button
          v-if="auditId && status === 'running'"
          data-testid="cancel-current-audit"
          type="danger"
          plain
          :loading="cancellingIds.has(auditId)"
          @click="terminateAudit(auditId)"
        >
          终止审计
        </el-button>
      </div>

      <div v-if="parallelAudits.length" class="parallel-tasks" data-testid="parallel-audits">
        <div class="parallel-tasks__header">
          <div>
            <span class="panel-index">PARALLEL TASKS</span>
            <strong>{{ parallelAudits.length }} 个任务正在并行或排队</strong>
          </div>
          <span>点击任务切换实时管线</span>
        </div>
        <div class="parallel-tasks__list">
          <article
            v-for="task in parallelAudits"
            :key="task.id"
            class="parallel-task"
            :class="{ 'parallel-task--selected': task.id === auditId }"
            data-testid="parallel-task"
            tabindex="0"
            :aria-current="task.id === auditId ? 'true' : undefined"
            @click="switchAudit(task)"
            @keydown.enter="switchAudit(task)"
          >
            <div class="parallel-task__main">
              <strong>#{{ task.id }} · {{ tokenName(task.tokenId) }}</strong>
              <span>{{ task.executionState === "queued" ? "排队中" : "执行中" }} · {{ task.progress || 0 }}%</span>
            </div>
            <el-progress :percentage="task.progress || 0" :stroke-width="3" :show-text="false" />
            <el-button
              link
              type="danger"
              :loading="cancellingIds.has(task.id)"
              @click.stop="terminateAudit(task.id)"
            >
              终止
            </el-button>
          </article>
        </div>
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
          <el-button size="small" :loading="refreshing" :disabled="!auditId" @click="refreshOnce()">
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
        <div v-if="failureDetail" class="failure-detail" role="alert" data-testid="audit-failure-detail">
          <strong>失败原因</strong>
          <span>{{ failureDetail }}</span>
        </div>
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

      <ol class="terminal-window" role="log" aria-live="polite" aria-label="审计实时事件">
        <li v-if="!displayEvents.length" class="terminal-empty">
          <span class="terminal-prompt">$</span>
          <div>
            <strong>暂无审计事件</strong>
            <p>{{ auditId ? "等待后端返回下一条审计证据…" : "启动审计后，调用状态与耗时将在这里逐行显示。" }}</p>
          </div>
        </li>

        <li
          v-for="(row, index) in displayEvents"
          v-else
          :key="row.id ?? `${row.ts || 'event'}-${index}`"
          class="terminal-event"
          data-testid="terminal-event"
        >
          <div class="event-lead">
            <time :datetime="eventDatetime(row.ts)" data-testid="event-timestamp">{{ row.ts || "—" }}</time>
            <el-tag data-testid="event-tag" size="small" :type="eventTagType(row)">
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
        </li>
      </ol>
    </section>
  </div>
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import { cancelAudit, getAudit, getAuditAiConfig, listAuditEvents, listAudits, listTokens, startAudit } from "../request/api"
import { AUDIT_STAGES, stageLabel } from "../constants/auditStages"
import { readStorage, removeStorage, writeStorage } from "../utils/storage"

const router = useRouter()
const openAuditAiSettings = inject("openAuditAiSettings", () => {})
const tokens = ref([])
const tokenId = ref(null)
const exportFormats = ref(["json", "md", "xlsx"])
const loadingTokens = ref(true)
const tokenError = ref("")
const submitting = ref(false)
const parallelAudits = ref([])
const refreshingTasks = ref(false)
const cancellingIds = ref(new Set())

const auditId = ref(null)
const status = ref("")
const progress = ref(0)
const refreshing = ref(false)
const events = ref([])
const clearedThroughEventId = ref(null)
const clearedFallbackCounts = ref(new Map())
let pollTimer = null
let taskPollTimer = null
let componentAlive = true
let auditGeneration = 0
let refreshSequence = 0
let latestAppliedSequence = 0
let tokenRequestSequence = 0
const inFlightRefreshes = new Map()
const LAST_AUDIT_ID_KEY = "lastAuditId"
const validPhases = new Set(AUDIT_STAGES.map((stage) => stage.key))

function tokenName(id) {
  return tokens.value.find((token) => token.id === id)?.name || `Token ${id}`
}

function stageKeysForPhase(phase) {
  if (phase === "compliance_stability") return ["compliance", "stability"]
  return validPhases.has(phase) ? [phase] : []
}

function numericEventId(row) {
  if (row?.id === undefined || row?.id === null || row.id === "") return null
  const id = Number(row.id)
  return Number.isFinite(id) ? id : null
}

function stableEventValue(value) {
  if (Array.isArray(value)) return value.map(stableEventValue)
  if (!value || typeof value !== "object") return value
  return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableEventValue(value[key])]))
}

function fallbackEventKey(row) {
  return JSON.stringify(stableEventValue({ ts: row?.ts ?? null, event: row?.event ?? null, payload: row?.payload ?? null }))
}

const displayEvents = computed(() => {
  const fallbackSeen = new Map()
  const visible = events.value.filter((row) => {
    const id = numericEventId(row)
    if (id !== null) {
      return clearedThroughEventId.value === null || id > clearedThroughEventId.value
    }

    // Legacy rows have no id. Occurrence counts by stable value survive full-array replacements
    // and allow a genuinely new duplicate to appear without relying on a mutable array index.
    const key = fallbackEventKey(row)
    const occurrence = (fallbackSeen.get(key) || 0) + 1
    fallbackSeen.set(key, occurrence)
    return occurrence > (clearedFallbackCounts.value.get(key) || 0)
  })
  return visible.slice(-200)
})

const stageProgress = computed(() => {
  const states = Object.fromEntries(
    AUDIT_STAGES.map((stage) => [stage.key, auditId.value ? "pending" : "ready"])
  )
  const activeStageKeys = []
  let latestStageKeys = []

  for (const row of events.value) {
    const phase = row?.payload?.phase
    const stageKeys = stageKeysForPhase(phase)
    if (!stageKeys.length) continue

    if (row.event === "phase_start" || (row.event === "deepseek_call_start" && phase === "overall")) {
      for (const key of stageKeys) {
        states[key] = "running"
        const priorIndex = activeStageKeys.indexOf(key)
        if (priorIndex !== -1) activeStageKeys.splice(priorIndex, 1)
        activeStageKeys.push(key)
      }
      latestStageKeys = stageKeys
      continue
    }

    if (row.event === "phase_end") {
      const endState = row.payload?.status === "error" ? "failed" : "completed"
      for (const key of stageKeys) {
        states[key] = endState
        const activeIndex = activeStageKeys.indexOf(key)
        if (activeIndex !== -1) activeStageKeys.splice(activeIndex, 1)
      }
      latestStageKeys = stageKeys
      continue
    }

    if (row.event === "deepseek_call_end" && phase === "overall") {
      states.overall = "completed"
      latestStageKeys = stageKeys
      const activeIndex = activeStageKeys.indexOf("overall")
      if (activeIndex !== -1) activeStageKeys.splice(activeIndex, 1)
    }
  }

  if (status.value === "completed") {
    for (const stage of AUDIT_STAGES) {
      if (states[stage.key] === "running") states[stage.key] = "completed"
    }
    activeStageKeys.splice(0)
  } else if (status.value === "failed" || status.value === "cancelled") {
    for (const stage of AUDIT_STAGES) {
      if (states[stage.key] === "running") states[stage.key] = "failed"
    }
    activeStageKeys.splice(0)
  }

  return { states, activeStageKeys, latestStageKeys }
})

const currentStageLabel = computed(() => {
  const keys = stageProgress.value.activeStageKeys.length
    ? stageProgress.value.activeStageKeys
    : stageProgress.value.latestStageKeys
  return keys.length ? keys.map(stageLabel).join(" / ") : "-"
})

const statusText = computed(() => {
  if (status.value === "running") return "审计中"
  if (status.value === "completed") return "已完成"
  if (status.value === "failed") return "失败"
  if (status.value === "cancelled") return "已终止"
  return status.value || "准备就绪"
})
const statusTagType = computed(() => {
  if (status.value === "running") return "warning"
  if (status.value === "completed") return "success"
  if (status.value === "failed") return "danger"
  if (status.value === "cancelled") return "danger"
  return "info"
})
const progressHint = computed(() => {
  if (status.value === "running" && progress.value >= 95) return "正在生成综合结论与报告内容..."
  if (status.value === "running") return "正在执行多 Agent 审计与审计 AI 判定..."
  if (status.value === "completed") return "审计已完成，可进入报告页查看详情"
  if (status.value === "failed") return "审计失败，可查看事件列表定位失败位置"
  if (status.value === "cancelled") return "该审计已由用户终止，已停止后续模型调用"
  return ""
})

const failureDetail = computed(() => {
  if (status.value === "cancelled") return "任务已由用户终止，未生成完整审计报告"
  if (status.value !== "failed") return ""
  const failureEvent = [...events.value].reverse().find((row) =>
    row.event === "preflight_end" && row.payload?.status === "failed"
  ) || [...events.value].reverse().find((row) =>
    row.event === "audit_aborted" || row.event === "audit_failed"
  )
  const payload = failureEvent?.payload || {}
  return payload.message || payload.reason || payload.error || "审计任务失败，请查看事件列表"
})

function stageState(index) {
  return stageProgress.value.states[AUDIT_STAGES[index].key]
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
    const statusValue = payload.status_code === 0 ? "网络错误" : `HTTP ${payload.status_code}`
    details.push({ key: "status_code", label: "STATUS", value: statusValue })
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
  if (payload.status !== undefined && payload.status !== null) {
    details.push({ key: "status", label: "RESULT", value: payload.status })
  }
  if (payload.reason) details.push({ key: "reason", label: "REASON", value: payload.reason })
  if (payload.endpoint) details.push({ key: "endpoint", label: "ENDPOINT", value: payload.endpoint })
  if (payload.message) details.push({ key: "message", label: "MESSAGE", value: payload.message })
  return details
}

async function reloadTokens() {
  const requestSequence = ++tokenRequestSequence
  loadingTokens.value = true
  tokenError.value = ""
  try {
    const loadedTokens = await listTokens()
    if (!componentAlive || requestSequence !== tokenRequestSequence) return
    tokens.value = loadedTokens || []
    if (!tokens.value.some((token) => token.id === tokenId.value)) {
      tokenId.value = tokens.value[0]?.id ?? null
    }
  } catch (e) {
    if (!componentAlive || requestSequence !== tokenRequestSequence) return
    tokenError.value = e?.response?.data?.error || e?.message || "加载失败"
    ElMessage.error(tokenError.value)
  } finally {
    if (componentAlive && requestSequence === tokenRequestSequence) loadingTokens.value = false
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

function startPolling(id, generation, refreshImmediately = true) {
  stopPolling()
  pollTimer = setInterval(() => {
    refreshOnce(id, generation)
  }, 1200)
  if (refreshImmediately) refreshOnce(id, generation)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function ensureTaskPolling() {
  if (taskPollTimer || !parallelAudits.value.length) return
  taskPollTimer = setInterval(refreshParallelAudits, 2000)
}

function stopTaskPolling() {
  if (!taskPollTimer) return
  clearInterval(taskPollTimer)
  taskPollTimer = null
}

async function refreshParallelAudits() {
  if (refreshingTasks.value || !componentAlive) return
  refreshingTasks.value = true
  try {
    const rows = await listAudits()
    if (!componentAlive) return
    parallelAudits.value = (rows || []).filter((row) => row.status === "running")
    if (parallelAudits.value.length) ensureTaskPolling()
    else stopTaskPolling()
  } catch (error) {
    // The selected audit remains usable even if the compact task list cannot refresh.
  } finally {
    refreshingTasks.value = false
  }
}

async function switchAudit(task) {
  if (!task?.id || task.id === auditId.value) return
  stopPolling()
  auditGeneration += 1
  const generation = auditGeneration
  auditId.value = task.id
  status.value = task.status || "running"
  progress.value = task.progress || 0
  events.value = []
  clearedThroughEventId.value = null
  clearedFallbackCounts.value = new Map()
  saveLastAuditId(task.id)
  await refreshOnce(task.id, generation)
  if (componentAlive && auditId.value === task.id && status.value === "running") {
    startPolling(task.id, generation, false)
  }
}

async function terminateAudit(id) {
  if (!id || cancellingIds.value.has(id)) return
  try {
    await ElMessageBox.confirm(`确认终止审计 #${id}？正在进行的模型调用会立即停止。`, "终止审计", {
      type: "warning",
      confirmButtonText: "确认终止",
      cancelButtonText: "继续审计"
    })
  } catch (error) {
    if (error === "cancel" || error === "close") return
    ElMessage.error(error?.message || "终止确认失败")
    return
  }

  cancellingIds.value.add(id)
  try {
    const cancelled = await cancelAudit(id)
    if (!componentAlive) return
    ElMessage.success(`审计 #${id} 已终止`)
    parallelAudits.value = parallelAudits.value.filter((task) => task.id !== id)
    if (id === auditId.value) {
      stopPolling()
      status.value = cancelled?.status || "cancelled"
      progress.value = 100
      await refreshOnce(id, auditGeneration)
    }
    await refreshParallelAudits()
  } catch (error) {
    if (componentAlive) ElMessage.error(error?.response?.data?.error || error?.message || "终止审计失败")
  } finally {
    cancellingIds.value.delete(id)
  }
}

function refreshOnce(targetAuditId = auditId.value, targetGeneration = auditGeneration) {
  if (!targetAuditId || !componentAlive) return Promise.resolve()
  const existing = inFlightRefreshes.get(targetAuditId)
  if (existing?.generation === targetGeneration) return existing.promise

  const sequence = ++refreshSequence
  refreshing.value = true
  let promise
  promise = (async () => {
    try {
      const audit = await getAudit(targetAuditId)
      if (!componentAlive) return
      const auditEvents = await listAuditEvents(targetAuditId)
      const isCurrent =
        componentAlive &&
        auditId.value === targetAuditId &&
        auditGeneration === targetGeneration &&
        sequence > latestAppliedSequence
      if (!isCurrent) return

      latestAppliedSequence = sequence
      status.value = audit.status
      progress.value = audit.progress ?? 0
      events.value = auditEvents || []

      if (audit.status === "completed" || audit.status === "failed" || audit.status === "cancelled") {
        progress.value = 100
        stopPolling()
        clearLastAuditId()
        refreshParallelAudits()
      }
    } catch (e) {
      if (componentAlive && auditId.value === targetAuditId && auditGeneration === targetGeneration) {
        ElMessage.error(e?.response?.data?.error || e?.message || "刷新失败")
      }
    } finally {
      const entry = inFlightRefreshes.get(targetAuditId)
      if (entry?.promise === promise) inFlightRefreshes.delete(targetAuditId)
      if (componentAlive) {
        const current = inFlightRefreshes.get(auditId.value)
        refreshing.value = Boolean(current && current.generation === auditGeneration)
      }
    }
  })()
  inFlightRefreshes.set(targetAuditId, { generation: targetGeneration, promise })
  return promise
}

async function submit() {
  if (!tokenId.value) {
    ElMessage.warning("请先选择Token")
    return
  }
  submitting.value = true
  try {
    const aiConfig = await getAuditAiConfig()
    if (!aiConfig?.configured) {
      ElMessage.warning("请配置审计 API Key")
      openAuditAiSettings("请配置审计 API Key 后再开始审计。")
      return
    }
    const res = await startAudit({ tokenId: tokenId.value, exportFormats: exportFormats.value })
    if (!componentAlive) return
    stopPolling()
    auditGeneration += 1
    auditId.value = res.auditId
    saveLastAuditId(auditId.value)
    status.value = "running"
    progress.value = 0
    events.value = []
    clearedThroughEventId.value = null
    clearedFallbackCounts.value = new Map()
    ElMessage.success("已开始审计，正在实时更新进度")
    parallelAudits.value = [
      { id: auditId.value, tokenId: tokenId.value, status: "running", executionState: "queued", progress: 0 },
      ...parallelAudits.value.filter((task) => task.id !== auditId.value)
    ]
    ensureTaskPolling()
    startPolling(auditId.value, auditGeneration)
  } catch (e) {
    const errorCode = e?.response?.data?.error
    if (componentAlive && errorCode === "audit_ai_not_configured") {
      ElMessage.warning("请配置审计 API Key")
      openAuditAiSettings("审计 AI 配置不存在或已过期，请重新配置审计 API Key。")
    } else if (componentAlive) {
      ElMessage.error(errorCode || e?.message || "审计失败")
    }
  } finally {
    submitting.value = false
  }
}

function clearView() {
  const eventIds = events.value.map(numericEventId).filter((id) => id !== null)
  if (eventIds.length) {
    clearedThroughEventId.value = Math.max(clearedThroughEventId.value ?? -Infinity, ...eventIds)
  }

  const nextCounts = new Map(clearedFallbackCounts.value)
  const currentCounts = new Map()
  for (const row of events.value) {
    if (numericEventId(row) !== null) continue
    const key = fallbackEventKey(row)
    currentCounts.set(key, (currentCounts.get(key) || 0) + 1)
  }
  for (const [key, count] of currentCounts) {
    nextCounts.set(key, Math.max(nextCounts.get(key) || 0, count))
  }
  clearedFallbackCounts.value = nextCounts
}

function eventTagType(row) {
  const ev = typeof row === "string" ? row : row?.event
  if (ev === "preflight_end") return row?.payload?.status === "passed" ? "success" : "danger"
  if (ev === "audit_aborted") return "danger"
  if (ev === "token_call_end") return "info"
  if (ev === "deepseek_call_end") return "success"
  if (ev === "audit_failed") return "danger"
  if (ev === "audit_cancelled") return "danger"
  if (ev === "audit_completed") return "success"
  if (ev === "phase_start") return "warning"
  return "info"
}

function eventDatetime(value) {
  if (!value) return undefined
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString()
}

function eventText(row) {
  const ev = row.event
  const p = row.payload || {}
  if (ev === "preflight_start") return `开始中转站连通预检：${p.model || ""}`
  if (ev === "preflight_end") return p.status === "passed"
    ? `中转站预检通过：HTTP ${p.status_code}，耗时 ${p.elapsed_ms}ms`
    : `中转站预检失败：${p.message || p.reason || "无法连通"}`
  if (ev === "audit_aborted") return `已停止审计：${p.message || p.reason || "前置预检失败"}`
  if (ev === "phase_start") return `开始阶段：${p.phase || ""}`
  if (ev === "phase_end") return `结束阶段：${p.phase || ""}`
  if (ev === "token_call_start") return `调用中转模型：${p.model || ""} ${p.scenario ? `(${p.scenario})` : ""}`
  if (ev === "token_call_end") return `中转返回：status=${p.status_code} 耗时=${p.elapsed_ms}ms`
  if (ev === "deepseek_call_start") return `审计 AI 判定：${p.model || ""}`
  if (ev === "deepseek_call_end") return `审计 AI 返回：耗时=${p.elapsed_ms}ms`
  if (ev === "audit_start") return "开始审计任务"
  if (ev === "audit_completed") return `审计完成：${p.overallConclusion || ""}`
  if (ev === "audit_failed") return `审计失败：${p.error || ""}`
  if (ev === "audit_cancelled") return `审计已终止：${p.message || "用户主动终止"}`
  return JSON.stringify(p)
}

onMounted(reloadTokens)
onMounted(refreshParallelAudits)
onMounted(async () => {
  const lastId = loadLastAuditId()
  if (!lastId) return
  auditGeneration += 1
  const restoredGeneration = auditGeneration
  auditId.value = lastId
  await refreshOnce(lastId, restoredGeneration)
  if (
    componentAlive &&
    auditGeneration === restoredGeneration &&
    auditId.value === lastId &&
    status.value === "running"
  ) {
    startPolling(lastId, restoredGeneration, false)
  }
})

onBeforeUnmount(() => {
  componentAlive = false
  auditGeneration += 1
  tokenRequestSequence += 1
  stopPolling()
  stopTaskPolling()
  cancellingIds.value.clear()
  inFlightRefreshes.clear()
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

.parallel-tasks { padding: 11px 14px 14px; border-top: 1px solid var(--ta-line); background: rgba(67, 224, 162, .018); }
.parallel-tasks__header { display: flex; align-items: end; justify-content: space-between; gap: 16px; margin-bottom: 9px; color: var(--ta-faint); font-family: var(--ta-mono); font-size: 9px; }
.parallel-tasks__header strong { display: block; color: var(--ta-text); font-size: 11px; font-weight: 600; }
.parallel-tasks__list { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 7px; }
.parallel-task { position: relative; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px 10px; padding: 9px 10px; background: var(--ta-code); border: 1px solid var(--ta-line); border-radius: 4px; cursor: pointer; transition: border-color 160ms ease, background 160ms ease, transform 160ms ease; }
.parallel-task:hover, .parallel-task:focus-visible, .parallel-task--selected { outline: none; background: rgba(67, 224, 162, .045); border-color: rgba(67, 224, 162, .34); transform: translateY(-1px); }
.parallel-task__main { display: grid; min-width: 0; gap: 3px; }
.parallel-task__main strong, .parallel-task__main span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.parallel-task__main strong { color: var(--ta-text); font-size: 10px; font-weight: 600; }
.parallel-task__main span { color: var(--ta-faint); font-family: var(--ta-mono); font-size: 9px; }
.parallel-task :deep(.el-progress) { grid-column: 1 / -1; }
.parallel-task :deep(.el-button) { grid-column: 2; grid-row: 1; align-self: center; margin: 0; padding: 0; font-size: 10px; }

.pipeline-panel--running {
  border-color: rgba(233, 187, 99, 0.25);
}

.pipeline-panel--completed {
  border-color: rgba(67, 224, 162, 0.32);
}

.pipeline-panel--failed {
  border-color: rgba(255, 125, 121, 0.34);
}

.pipeline-panel--cancelled { border-color: rgba(255, 125, 121, 0.34); }

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

.status-chip--cancelled { color: var(--ta-danger); border-color: rgba(255, 125, 121, 0.32); }

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

.failure-detail {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 8px 12px;
  margin-top: 10px;
  padding: 9px 10px;
  color: var(--ta-danger);
  background: rgba(255, 125, 121, 0.055);
  border: 1px solid rgba(255, 125, 121, 0.22);
  border-radius: 4px;
  font-size: 11px;
}

.failure-detail strong {
  font-family: var(--ta-mono);
  font-size: 10px;
  letter-spacing: 0.04em;
}

.failure-detail span {
  overflow-wrap: anywhere;
  color: var(--ta-text);
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
  margin: 0;
  padding: 0;
  background:
    linear-gradient(rgba(67, 224, 162, 0.018) 1px, transparent 1px),
    var(--ta-code);
  background-size: 100% 28px;
  font-family: var(--ta-mono);
  list-style: none;
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

@media (max-width: 900px) {
  .configuration-grid {
    grid-template-columns: 1fr;
  }

  .format-field {
    border-top: 1px solid var(--ta-line);
    border-left: 0;
  }
}

@media (max-width: 840px) {
  .audit-heading {
    align-items: flex-start;
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
