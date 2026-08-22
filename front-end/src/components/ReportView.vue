<template>
  <div class="report-console">
    <header v-reveal class="report-heading">
      <div>
        <div class="eyebrow"><span class="signal-dot" aria-hidden="true"></span> AUDIT REPORT</div>
        <h1 data-testid="report-title">审计报告 <span>#{{ auditId }}</span></h1>
        <p>基于真实调用事件生成的六维 Token 安全审计结果</p>
      </div>
      <div class="heading-actions">
        <el-button :loading="refreshing" @click="refreshOnce()">刷新</el-button>
        <el-button :disabled="!markdown" type="primary" @click="copyMarkdown">复制 Markdown</el-button>
        <el-button @click="$router.push('/history')">返回历史</el-button>
      </div>
    </header>

    <section v-if="loading" class="console-panel loading-panel" aria-label="正在加载报告">
      <el-skeleton :rows="10" animated />
    </section>

    <template v-else>
      <section v-reveal class="console-panel overview-panel">
        <div class="panel-header">
          <div>
            <span class="panel-index">01 / OVERVIEW</span>
            <h2>报告状态</h2>
          </div>
          <span class="status-chip" :class="`status-chip--${status || 'unknown'}`">{{ statusText }}</span>
        </div>

        <div class="overview-grid">
          <dl class="report-meta">
            <div><dt>REPORT ID</dt><dd>#{{ auditId }}</dd></div>
            <div><dt>审计时间</dt><dd>{{ auditTime }}</dd></div>
            <div><dt>平台</dt><dd>{{ baseInfo?.platform || "-" }}</dd></div>
            <div><dt>宣称模型</dt><dd>{{ baseInfo?.claimed_model || "-" }}</dd></div>
            <div><dt>TOKEN</dt><dd>{{ baseInfo?.token_masked || "-" }}</dd></div>
            <div><dt>事件数量</dt><dd>{{ events.length }}</dd></div>
          </dl>
          <div class="progress-block">
            <div class="progress-copy">
              <strong>{{ progress }}%</strong>
              <span>{{ progressHint }}</span>
            </div>
            <el-progress :percentage="progress" :stroke-width="7" :show-text="false" />
            <p v-if="failureMessage" class="failure-message">{{ failureMessage }}</p>
          </div>
        </div>
      </section>

      <section v-reveal="{ stagger: 70 }" class="console-panel conclusion-panel">
        <div class="panel-header">
          <div>
            <span class="panel-index">02 / VERDICT</span>
            <h2>综合结论</h2>
          </div>
          <span class="panel-note">先看结论，再核对分项证据</span>
        </div>
        <div class="conclusion-copy" data-testid="overall-conclusion">
          <span class="verdict-mark" aria-hidden="true">∴</span>
          <p>{{ overallConclusion }}</p>
        </div>
        <div class="advice-grid">
          <article class="advice-card advice-card--risk">
            <div class="advice-heading"><span>!</span><h3>风险警示</h3></div>
            <ul data-testid="risk-list">
              <li v-for="(item, index) in riskWarnings" :key="`risk-${index}`">{{ item }}</li>
              <li v-if="!riskWarnings.length" class="empty-line">暂无明确风险警示</li>
            </ul>
          </article>
          <article class="advice-card advice-card--suggestion">
            <div class="advice-heading"><span>→</span><h3>使用建议</h3></div>
            <ul data-testid="suggestion-list">
              <li v-for="(item, index) in usageSuggestions" :key="`suggestion-${index}`">{{ item }}</li>
              <li v-if="!usageSuggestions.length" class="empty-line">暂无额外使用建议</li>
            </ul>
          </article>
        </div>
      </section>

      <section v-reveal="{ stagger: 140 }" class="console-panel dimensions-panel">
        <div class="panel-header">
          <div>
            <span class="panel-index">03 / DIMENSIONS</span>
            <h2>六个维度</h2>
          </div>
          <span class="panel-note">按审计执行口径固定排序</span>
        </div>
        <div class="dimension-grid">
          <article
            v-for="(dimension, index) in dimensions"
            :key="dimension.key"
            class="dimension-card"
            data-testid="report-dimension"
            :data-dimension="dimension.key"
          >
            <div class="dimension-heading">
              <span>{{ String(index + 1).padStart(2, "0") }}</span>
              <h3>{{ dimension.label }}</h3>
            </div>
            <p class="dimension-conclusion">{{ dimension.conclusion }}</p>
            <div class="dimension-evidence">
              <span>EVIDENCE</span>
              <p>{{ dimension.evidence }}</p>
            </div>
          </article>
        </div>
      </section>

      <section v-reveal="{ stagger: 210 }" class="console-panel data-panel">
        <div class="panel-header data-header">
          <div>
            <span class="panel-index">04 / EVIDENCE</span>
            <h2>报告原文与原始数据</h2>
          </div>
          <div class="tab-list" role="tablist" aria-label="报告数据视图">
            <button :class="{ active: tab === 'md' }" role="tab" :aria-selected="tab === 'md'" @click="tab = 'md'">Markdown</button>
            <button :class="{ active: tab === 'json' }" role="tab" :aria-selected="tab === 'json'" @click="tab = 'json'">JSON</button>
            <button :class="{ active: tab === 'events' }" role="tab" :aria-selected="tab === 'events'" @click="tab = 'events'">事件</button>
          </div>
        </div>

        <pre v-if="tab === 'md'" class="code-output" data-testid="markdown-output">{{ markdown || "报告尚未生成。审计完成后，Markdown 原文会显示在这里。" }}</pre>
        <pre v-else-if="tab === 'json'" class="code-output" data-testid="json-output">{{ jsonText }}</pre>
        <div v-else class="event-terminal" data-testid="event-output">
          <div v-if="!events.length" class="terminal-empty"><span>$</span> 尚无审计事件</div>
          <ol v-else>
            <li v-for="row in recentEvents" :key="row.id || `${row.ts}-${row.event}`">
              <time :datetime="eventDatetime(row.ts)">{{ row.ts || "--" }}</time>
              <strong>{{ row.event || "event" }}</strong>
              <span>{{ eventText(row) }}</span>
            </li>
          </ol>
        </div>
      </section>

      <section v-if="exportRows.length" v-reveal="{ stagger: 280 }" class="console-panel export-panel">
        <div class="panel-header">
          <div>
            <span class="panel-index">05 / EXPORTS</span>
            <h2>导出文件</h2>
          </div>
        </div>
        <dl class="export-list">
          <div v-for="item in exportRows" :key="item.format"><dt>{{ item.format }}</dt><dd>{{ item.path }}</dd></div>
        </dl>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue"
import { ElMessage } from "element-plus"
import { AUDIT_STAGES } from "../constants/auditStages"
import { getAudit, listAuditEvents } from "../request/api"
import { prettyJson } from "../utils/format"

const props = defineProps({
  auditId: { type: Number, required: true }
})

const loading = ref(true)
const refreshing = ref(false)
const report = ref(null)
const events = ref([])
const tab = ref("md")
const inFlightRefreshes = new Map()
let pollTimer = null
let reportGeneration = 0
let refreshSequence = 0
let latestAppliedSequence = 0
let componentAlive = true

const status = computed(() => report.value?.status || "")
const progress = computed(() => Math.min(100, Math.max(0, Number(report.value?.progress) || 0)))
const statusText = computed(() => ({ running: "审计中", completed: "已完成", failed: "失败" })[status.value] || status.value || "等待数据")
const progressHint = computed(() => {
  if (status.value === "running" && progress.value >= 95) return "正在生成综合结论与报告内容"
  if (status.value === "running") return "六维审计正在执行"
  if (status.value === "completed") return "报告已生成"
  if (status.value === "failed") return "任务已中断"
  return "等待后端状态"
})

const reportBody = computed(() => report.value?.report || {})
const baseInfo = computed(() => reportBody.value?.base_info || null)
const overall = computed(() => reportBody.value?.overall || {})
const auditTime = computed(() => baseInfo.value?.audit_time || report.value?.auditTime || "-")
const overallConclusion = computed(() => report.value?.overallConclusion || overall.value?.overall_conclusion || (status.value === "running" ? "审计仍在运行，综合结论将在六维审计完成后生成。" : "暂无综合结论。"))
const riskWarnings = computed(() => asTextList(overall.value?.risk_warnings))
const usageSuggestions = computed(() => asTextList(overall.value?.usage_suggestions))
const markdown = computed(() => reportBody.value?.report_markdown || reportBody.value?.reportMarkdown || "")
const jsonText = computed(() => prettyJson(report.value || {}))
const failureMessage = computed(() => status.value === "failed" ? textValue(reportBody.value?.error, "未返回失败原因") : "")
const recentEvents = computed(() => events.value.slice(-120))
const exportRows = computed(() => Object.entries(reportBody.value?.exports || {}).filter(([, path]) => path).map(([format, path]) => ({ format: format.toUpperCase(), path: String(path) })))
const dimensions = computed(() => {
  const sections = reportBody.value?.sections || {}
  return AUDIT_STAGES.filter((stage) => stage.key !== "overall").map((stage) => {
    const section = sections[stage.key] || {}
    return {
      ...stage,
      conclusion: textValue(section.conclusion, status.value === "running" ? "等待该维度完成" : "未返回分项结论"),
      evidence: textValue(section.evidence, "暂无可展示证据")
    }
  })
})

function asTextList(value) {
  if (Array.isArray(value)) return value.map((item) => textValue(item, "")).filter(Boolean)
  if (value === null || value === undefined || value === "") return []
  return [textValue(value, "")].filter(Boolean)
}

function textValue(value, fallback) {
  if (value === null || value === undefined || value === "") return fallback
  if (typeof value === "string") return value
  return prettyJson(value)
}

function beginAuditLoad(id) {
  stopPolling()
  reportGeneration += 1
  latestAppliedSequence = 0
  report.value = null
  events.value = []
  loading.value = true
  const generation = reportGeneration
  refreshOnce(id, generation, true).then(() => {
    if (!componentAlive || generation !== reportGeneration || id !== props.auditId) return
    loading.value = false
    if (status.value === "running") startPolling(id, generation)
  })
}

function startPolling(id, generation) {
  stopPolling()
  pollTimer = setInterval(() => refreshOnce(id, generation), 1500)
}

function stopPolling() {
  if (!pollTimer) return
  clearInterval(pollTimer)
  pollTimer = null
}

function refreshOnce(targetAuditId = props.auditId, targetGeneration = reportGeneration, initial = false) {
  if (!componentAlive || !Number.isFinite(targetAuditId) || targetAuditId <= 0) return Promise.resolve()
  const existing = inFlightRefreshes.get(targetAuditId)
  if (existing?.generation === targetGeneration) return existing.promise

  const sequence = ++refreshSequence
  refreshing.value = !initial
  let promise
  promise = (async () => {
    try {
      const nextReport = await getAudit(targetAuditId)
      if (!componentAlive || targetGeneration !== reportGeneration || targetAuditId !== props.auditId) return
      const nextEvents = await listAuditEvents(targetAuditId)
      const isCurrent = componentAlive && targetGeneration === reportGeneration && targetAuditId === props.auditId && sequence > latestAppliedSequence
      if (!isCurrent) return

      latestAppliedSequence = sequence
      report.value = nextReport
      events.value = nextEvents || []
      if (nextReport?.status === "completed" || nextReport?.status === "failed") stopPolling()
    } catch (error) {
      if (componentAlive && targetGeneration === reportGeneration && targetAuditId === props.auditId) {
        ElMessage.error(error?.response?.data?.error || error?.message || "报告加载失败")
      }
    } finally {
      const entry = inFlightRefreshes.get(targetAuditId)
      if (entry?.promise === promise) inFlightRefreshes.delete(targetAuditId)
      if (componentAlive && targetGeneration === reportGeneration && targetAuditId === props.auditId) {
        refreshing.value = false
        if (initial) loading.value = false
      }
    }
  })()
  inFlightRefreshes.set(targetAuditId, { generation: targetGeneration, promise })
  return promise
}

function eventDatetime(value) {
  if (!value) return undefined
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString()
}

function eventText(row) {
  const event = row.event
  const payload = row.payload || {}
  if (event === "preflight_start") return `开始中转站连通预检：${payload.model || "-"}`
  if (event === "preflight_end") return payload.status === "passed"
    ? `中转站预检通过：HTTP ${payload.status_code ?? "-"} · ${payload.elapsed_ms ?? "-"}ms`
    : `中转站预检失败：${payload.message || payload.reason || "无法连通"}`
  if (event === "audit_aborted") return `已停止审计：${payload.message || payload.reason || "前置预检失败"}`
  if (event === "phase_start") return `开始阶段：${payload.phase || "-"}`
  if (event === "phase_end") return `结束阶段：${payload.phase || "-"}${payload.status ? ` · ${payload.status}` : ""}`
  if (event === "token_call_start") return `调用中转模型：${payload.model || "-"}${payload.scenario ? ` · ${payload.scenario}` : ""}`
  if (event === "token_call_end") return `中转返回：status=${payload.status_code ?? "-"} · ${payload.elapsed_ms ?? "-"}ms`
  if (event === "deepseek_call_start") return `开始综合判定：${payload.model || "-"}`
  if (event === "deepseek_call_end") return `综合判定返回：${payload.elapsed_ms ?? "-"}ms`
  if (event === "audit_start") return "开始审计任务"
  if (event === "audit_completed") return `审计完成：${payload.overallConclusion || "已生成报告"}`
  if (event === "audit_failed") return `审计失败：${payload.error || "未知错误"}`
  return textValue(payload, "-")
}

async function copyMarkdown() {
  if (!markdown.value) return
  try {
    await navigator.clipboard.writeText(markdown.value)
    ElMessage.success("Markdown 已复制")
  } catch {
    ElMessage.warning("复制失败，请手动选中复制")
  }
}

watch(() => props.auditId, (id) => beginAuditLoad(id), { immediate: true })

onBeforeUnmount(() => {
  componentAlive = false
  reportGeneration += 1
  stopPolling()
  inFlightRefreshes.clear()
})
</script>

<style scoped>
.report-console { display: grid; gap: 14px; width: 100%; max-width: 1440px; margin: 0 auto; }
.report-heading, .panel-header, .heading-actions, .dimension-heading, .advice-heading, .progress-copy { display: flex; align-items: center; }
.report-heading { justify-content: space-between; gap: 24px; padding: 6px 0 10px; border-bottom: 1px solid var(--ta-line); }
.eyebrow, .panel-index, .panel-note, .status-chip, .report-meta, .dimension-heading span, .dimension-evidence span, .tab-list, .code-output, .event-terminal, .export-list { font-family: var(--ta-mono); }
.eyebrow { display: flex; gap: 8px; align-items: center; color: var(--ta-green); font-size: 11px; letter-spacing: .08em; }
.signal-dot { width: 6px; height: 6px; background: var(--ta-green); border-radius: 50%; box-shadow: 0 0 10px rgba(67,224,162,.58); }
.report-heading h1 { margin: 5px 0 2px; color: var(--ta-text); font-size: clamp(24px, 3vw, 34px); font-weight: 650; letter-spacing: -.035em; }
.report-heading h1 span { color: var(--ta-green); font-family: var(--ta-mono); font-size: .68em; font-weight: 500; }
.report-heading p { margin: 0; color: var(--ta-muted); font-size: 13px; }
.heading-actions { justify-content: flex-end; gap: 8px; flex-wrap: wrap; }
.console-panel { overflow: hidden; background: var(--ta-panel); border: 1px solid var(--ta-line); border-radius: var(--ta-radius); }
.loading-panel { padding: 18px; }
.panel-header { justify-content: space-between; gap: 18px; min-height: 58px; padding: 11px 14px; background: var(--ta-panel-raised); border-bottom: 1px solid var(--ta-line); }
.panel-index { display: block; margin-bottom: 2px; color: var(--ta-green); font-size: 10px; letter-spacing: .1em; }
.panel-header h2 { margin: 0; color: var(--ta-text); font-size: 15px; font-weight: 650; }
.panel-note { color: var(--ta-faint); font-size: 10px; }
.status-chip { padding: 3px 8px; color: var(--ta-faint); background: var(--ta-code); border: 1px solid var(--ta-line); border-radius: 4px; font-size: 10px; letter-spacing: .05em; }
.status-chip--running { color: var(--ta-amber); border-color: rgba(233,187,99,.28); }
.status-chip--completed { color: var(--ta-green); border-color: rgba(67,224,162,.32); }
.status-chip--failed { color: var(--ta-danger); border-color: rgba(255,125,121,.32); }
.overview-grid { display: grid; grid-template-columns: minmax(0,1.4fr) minmax(280px,.6fr); }
.report-meta { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); margin: 0; background: var(--ta-line); gap: 1px; }
.report-meta div { min-width: 0; padding: 12px 14px; background: var(--ta-panel); }
.report-meta dt { color: var(--ta-faint); font-size: 9px; letter-spacing: .07em; }
.report-meta dd { overflow-wrap: anywhere; margin: 3px 0 0; color: var(--ta-text); font-size: 11px; }
.progress-block { padding: 18px; border-left: 1px solid var(--ta-line); }
.progress-copy { justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.progress-copy strong { color: var(--ta-green); font-family: var(--ta-mono); font-size: 22px; font-weight: 600; }
.progress-copy span { color: var(--ta-muted); font-size: 11px; text-align: right; }
.failure-message { margin: 10px 0 0; color: var(--ta-danger); font-family: var(--ta-mono); font-size: 10px; }
.conclusion-copy { display: grid; grid-template-columns: 34px minmax(0,1fr); gap: 12px; padding: 18px; border-bottom: 1px solid var(--ta-line); }
.verdict-mark { color: var(--ta-green); font-family: var(--ta-mono); font-size: 24px; }
.conclusion-copy p { margin: 1px 0 0; color: var(--ta-text); font-size: 14px; line-height: 1.75; }
.advice-grid { display: grid; grid-template-columns: 1fr 1fr; }
.advice-card { min-width: 0; padding: 15px 18px; }
.advice-card + .advice-card { border-left: 1px solid var(--ta-line); }
.advice-heading { gap: 8px; }
.advice-heading span { display: grid; width: 20px; height: 20px; place-items: center; border: 1px solid currentColor; border-radius: 4px; font-family: var(--ta-mono); font-size: 11px; }
.advice-heading h3 { margin: 0; color: var(--ta-text); font-size: 12px; font-weight: 650; }
.advice-card--risk .advice-heading { color: var(--ta-danger); }
.advice-card--suggestion .advice-heading { color: var(--ta-green); }
.advice-card ul { display: grid; gap: 7px; margin: 12px 0 0; padding-left: 18px; color: var(--ta-muted); font-size: 11px; line-height: 1.6; }
.advice-card--risk li::marker { color: var(--ta-danger); }
.advice-card--suggestion li::marker { color: var(--ta-green); }
.empty-line { color: var(--ta-faint); }
.dimension-grid { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 1px; background: var(--ta-line); }
.dimension-card { min-width: 0; min-height: 184px; padding: 15px; background: var(--ta-panel); }
.dimension-card:hover { background: rgba(67,224,162,.025); }
.dimension-heading { gap: 9px; }
.dimension-heading span { display: grid; width: 26px; height: 23px; place-items: center; color: var(--ta-green); background: var(--ta-code); border: 1px solid var(--ta-line-strong); border-radius: 4px; font-size: 9px; }
.dimension-heading h3 { margin: 0; color: var(--ta-text); font-size: 12px; font-weight: 650; }
.dimension-conclusion { min-height: 42px; margin: 14px 0; color: var(--ta-text); font-size: 12px; line-height: 1.65; }
.dimension-evidence { padding-top: 10px; border-top: 1px solid var(--ta-line); }
.dimension-evidence span { color: var(--ta-faint); font-size: 8px; letter-spacing: .08em; }
.dimension-evidence p { margin: 5px 0 0; color: var(--ta-muted); font-size: 10px; line-height: 1.6; white-space: pre-wrap; }
.data-header { align-items: flex-end; }
.tab-list { display: flex; gap: 4px; }
.tab-list button { padding: 5px 9px; color: var(--ta-faint); background: var(--ta-code); border: 1px solid var(--ta-line); border-radius: 4px; cursor: pointer; font: inherit; font-size: 9px; }
.tab-list button:hover, .tab-list button.active { color: var(--ta-green); border-color: var(--ta-line-strong); }
.code-output { min-height: 320px; max-height: 620px; overflow: auto; margin: 0; padding: 16px; color: var(--ta-muted); background: var(--ta-code); font-size: 11px; line-height: 1.7; white-space: pre-wrap; overflow-wrap: anywhere; }
.event-terminal { max-height: 520px; overflow: auto; color: var(--ta-muted); background: var(--ta-code); font-size: 10px; }
.event-terminal ol { min-width: 780px; margin: 0; padding: 0; list-style: none; }
.event-terminal li { display: grid; grid-template-columns: 210px 180px minmax(300px,1fr); gap: 12px; padding: 9px 14px; border-bottom: 1px solid var(--ta-line); }
.event-terminal time { color: var(--ta-faint); }
.event-terminal strong { color: var(--ta-green); font-weight: 500; }
.terminal-empty { min-height: 160px; padding: 24px; color: var(--ta-faint); }
.terminal-empty span { margin-right: 8px; color: var(--ta-green); }
.export-list { margin: 0; }
.export-list div { display: grid; grid-template-columns: 120px minmax(0,1fr); gap: 12px; padding: 10px 14px; border-bottom: 1px solid var(--ta-line); }
.export-list div:last-child { border-bottom: 0; }
.export-list dt { color: var(--ta-green); font-size: 10px; }
.export-list dd { overflow-wrap: anywhere; margin: 0; color: var(--ta-muted); font-size: 10px; }
@media (max-width: 960px) { .overview-grid { grid-template-columns: 1fr; } .progress-block { border-top: 1px solid var(--ta-line); border-left: 0; } .dimension-grid { grid-template-columns: repeat(2,minmax(0,1fr)); } }
@media (max-width: 680px) { .report-heading, .panel-header { align-items: stretch; flex-direction: column; } .heading-actions { justify-content: stretch; } .heading-actions :deep(.el-button) { flex: 1 1 calc(50% - 4px); margin-left: 0; } .report-meta, .dimension-grid, .advice-grid { grid-template-columns: 1fr; } .advice-card + .advice-card { border-top: 1px solid var(--ta-line); border-left: 0; } .data-header { align-items: stretch; } .tab-list { display: grid; grid-template-columns: repeat(3,1fr); } }
@media (max-width: 420px) { .report-meta { grid-template-columns: 1fr; } .conclusion-copy { grid-template-columns: 1fr; } }
</style>
