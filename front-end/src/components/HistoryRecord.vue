<template>
  <div class="history-console">
    <section v-reveal class="page-heading" aria-labelledby="history-page-title">
      <div>
        <div class="eyebrow"><span class="signal-dot" />AUDIT ARCHIVE / 审计档案</div>
        <h1 id="history-page-title">历史记录</h1>
        <p>按审计 ID 回溯任务状态、进度与最终报告。</p>
      </div>
      <el-button :loading="loading" @click="reload">刷新记录</el-button>
    </section>

    <section v-reveal class="console-panel" aria-labelledby="history-list-title">
      <header class="panel-header">
        <div>
          <span class="panel-index">01 / AUDIT LOG</span>
          <h2 id="history-list-title">审计任务索引</h2>
        </div>
        <span class="record-count">{{ records.length }} RECORDS</span>
      </header>

      <div v-if="operationError" data-testid="history-operation-error" class="operation-error" role="alert">
        {{ operationError }}
      </div>

      <div v-if="loading" data-testid="history-loading" class="state-panel" role="status" aria-live="polite">
        <span class="state-prompt">$</span>
        <div><strong>正在加载审计记录</strong><p>正在读取历史任务索引…</p></div>
      </div>

      <div v-else-if="loadError" data-testid="history-error" class="state-panel state-panel--error" role="alert">
        <span class="state-prompt">!</span>
        <div><strong>历史记录加载失败</strong><p>{{ loadError }}</p><el-button size="small" @click="reload">重试</el-button></div>
      </div>

      <div v-else-if="records.length === 0" data-testid="history-empty" class="state-panel" role="status">
        <span class="state-prompt">_</span>
        <div>
          <strong>暂无审计记录</strong>
          <p>发起首个审计后，任务状态与报告入口会显示在这里。</p>
          <el-button type="primary" size="small" @click="router.push('/audit')">快速审计</el-button>
        </div>
      </div>

      <div v-else data-testid="history-table" class="table-scroll" tabindex="0" aria-label="审计历史列表，可横向滚动">
        <el-table :data="records" class="compact-table" style="width: 100%">
          <el-table-column label="审计 ID" width="94">
            <template #default="{ row }">
              <span class="audit-id-cell">
                <code class="mono-value">#{{ row.id }}</code>
                <span v-if="unreadIds.has(Number(row.id))" class="row-unread-dot" title="报告尚未查看" aria-label="未查看报告" />
              </span>
            </template>
          </el-table-column>
          <el-table-column label="Token ID" width="100">
            <template #default="{ row }"><code class="mono-value">{{ row.tokenId }}</code></template>
          </el-table-column>
          <el-table-column label="审计类型" width="116">
            <template #default="{ row }">
              <span class="mode-badge" :class="`mode-badge--${auditMode(row)}`">
                {{ auditMode(row) === "deep" ? "深度审计" : "快速审计" }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="auditTime" label="审计时间" min-width="174" />
          <el-table-column label="状态" width="118">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small" class="status-badge" :class="`status-badge--${row.status || 'unknown'}`">
                {{ row.status || "unknown" }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="进度" width="138">
            <template #default="{ row }">
              <div class="progress-cell">
                <el-progress :percentage="Number(row.progress || 0)" :stroke-width="5" :show-text="false" />
                <span>{{ Number(row.progress || 0) }}%</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="综合结论" min-width="250">
            <template #default="{ row }">
              <span class="conclusion-text" :title="row.overallConclusion || '暂无结论'">
                {{ row.overallConclusion || "暂无结论" }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="178">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button type="primary" plain size="small" @click="open(row.id)">查看报告</el-button>
                <el-button
                  type="danger"
                  plain
                  size="small"
                  :loading="deletingIds.has(row.id)"
                  :disabled="row.status === 'running'"
                  :title="row.status === 'running' ? '请先终止正在运行的审计' : '删除该审计及其事实事件'"
                  @click="remove(row)"
                >删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import { deleteAudit, listAudits } from "../request/api"
import {
  AUDIT_READ_STATE_EVENT,
  markAllAuditReportsRead,
  markAuditReportRead,
  unreadAuditReportIds
} from "../utils/auditReadState"

const router = useRouter()
const records = ref([])
const loading = ref(true)
const loadError = ref("")
const operationError = ref("")
const unreadIds = ref(new Set())
const deletingIds = ref(new Set())
let requestSequence = 0
let componentAlive = true

async function reload() {
  const sequence = ++requestSequence
  loading.value = true
  loadError.value = ""
  records.value = []
  try {
    const loadedRecords = await listAudits()
    if (!componentAlive || sequence !== requestSequence) return
    records.value = loadedRecords || []
  } catch (error) {
    if (!componentAlive || sequence !== requestSequence) return
    loadError.value = error?.response?.data?.error || error?.message || "加载失败"
    ElMessage.error(loadError.value)
  } finally {
    if (componentAlive && sequence === requestSequence) loading.value = false
  }
}

function open(id) {
  unreadIds.value = markAuditReportRead(id)
  router.push(`/report/${id}`)
}

async function remove(row) {
  if (row.status === "running" || deletingIds.value.has(row.id)) return
  try {
    await ElMessageBox.confirm(
      `确认删除审计 #${row.id}？对应报告与事实事件也会一并删除，且无法恢复。`,
      "删除审计记录",
      { type: "warning", confirmButtonText: "删除", cancelButtonText: "取消" }
    )
  } catch (error) {
    if (error === "cancel" || error === "close") return
    operationError.value = error?.message || "删除确认失败"
    return
  }
  if (!componentAlive) return
  deletingIds.value.add(row.id)
  operationError.value = ""
  try {
    await deleteAudit(row.id)
    if (!componentAlive) return
    records.value = records.value.filter((item) => item.id !== row.id)
    unreadIds.value = markAuditReportRead(row.id)
    ElMessage.success(`审计 #${row.id} 已删除`)
  } catch (error) {
    if (!componentAlive) return
    operationError.value = error?.response?.data?.error || error?.message || "删除失败"
    ElMessage.error(operationError.value)
  } finally {
    if (componentAlive) deletingIds.value.delete(row.id)
  }
}

function auditMode(row) {
  return row?.auditMode === "deep" ? "deep" : "quick"
}

function syncUnreadIds() {
  unreadIds.value = unreadAuditReportIds()
}

function statusType(status) {
  if (status === "completed") return "success"
  if (status === "running") return "warning"
  if (status === "failed") return "danger"
  return "info"
}

onMounted(() => {
  unreadIds.value = markAllAuditReportsRead()
  window.addEventListener(AUDIT_READ_STATE_EVENT, syncUnreadIds)
  reload()
})
onBeforeUnmount(() => {
  componentAlive = false
  requestSequence += 1
  deletingIds.value.clear()
  window.removeEventListener(AUDIT_READ_STATE_EVENT, syncUnreadIds)
})
</script>

<style scoped>
.history-console { display: grid; gap: 14px; width: 100%; max-width: 1480px; margin: 0 auto; }
.page-heading { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 5px 0 10px; border-bottom: 1px solid var(--ta-line); }
.eyebrow, .panel-index, .record-count, .state-panel, .mono-value, .progress-cell span { font-family: var(--ta-mono); }
.eyebrow { display: flex; align-items: center; gap: 8px; color: var(--ta-green); font-size: 10px; letter-spacing: .08em; }
.signal-dot { width: 6px; height: 6px; background: var(--ta-green); border-radius: 50%; }
.page-heading h1 { margin: 4px 0 1px; color: var(--ta-text); font-size: clamp(23px, 2.8vw, 32px); font-weight: 650; letter-spacing: -.035em; }
.page-heading p { margin: 0; color: var(--ta-muted); font-size: 12px; }
.console-panel { min-width: 0; overflow: hidden; background: var(--ta-panel); border: 1px solid var(--ta-line); border-radius: var(--ta-radius); }
.panel-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 57px; padding: 10px 14px; background: var(--ta-panel-raised); border-bottom: 1px solid var(--ta-line); }
.panel-index { display: block; margin-bottom: 2px; color: var(--ta-green); font-size: 9px; letter-spacing: .1em; }
.panel-header h2 { margin: 0; color: var(--ta-text); font-size: 15px; font-weight: 650; }
.record-count { color: var(--ta-faint); font-size: 9px; letter-spacing: .08em; }
.state-panel { display: flex; gap: 12px; min-height: 220px; padding: 26px; color: var(--ta-muted); }
.state-prompt { color: var(--ta-green); }
.state-panel--error .state-prompt, .state-panel--error strong { color: var(--ta-danger); }
.state-panel strong { color: var(--ta-text); font-size: 12px; font-weight: 550; }
.state-panel p { margin: 5px 0 11px; color: var(--ta-faint); font-size: 10px; }
.table-scroll { overflow-x: auto; }
.compact-table { min-width: 1098px; }
.compact-table :deep(.el-table__cell) { padding: 8px 0; }
.compact-table :deep(.cell) { font-size: 11px; }
.mono-value { color: var(--ta-green); font-size: 10px; }
.audit-id-cell { display: inline-flex; align-items: center; gap: 7px; }
.row-unread-dot { width: 6px; height: 6px; flex: 0 0 auto; background: var(--ta-danger); border-radius: 50%; box-shadow: 0 0 8px rgba(255, 102, 112, .55); }
.row-actions { display: flex; gap: 6px; }
.row-actions :deep(.el-button) { margin-left: 0; }
.operation-error { margin: 10px 14px 0; padding: 8px 10px; color: var(--ta-danger); background: rgba(255, 125, 121, .055); border: 1px solid rgba(255, 125, 121, .2); border-radius: 4px; font-size: 11px; }
.mode-badge { display: inline-flex; padding: 3px 7px; color: var(--ta-muted); font-family: var(--ta-mono); font-size: 9px; letter-spacing: .04em; background: rgba(143, 159, 151, .07); border: 1px solid var(--ta-line); border-radius: 3px; }
.mode-badge--deep { color: #8eb9ff; background: rgba(94, 153, 255, .08); border-color: rgba(94, 153, 255, .22); }
.mode-badge--quick { color: var(--ta-green); background: rgba(67, 224, 162, .06); border-color: rgba(67, 224, 162, .18); }
.status-badge { font-family: var(--ta-mono); font-size: 9px; text-transform: uppercase; }
.status-badge--completed { color: var(--ta-green); }
.status-badge--running { color: var(--ta-amber); }
.status-badge--failed { color: var(--ta-danger); }
.progress-cell { display: grid; grid-template-columns: minmax(55px, 1fr) 34px; gap: 7px; align-items: center; }
.progress-cell span { color: var(--ta-muted); font-size: 9px; text-align: right; }
.conclusion-text { display: block; overflow: hidden; color: var(--ta-muted); text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 600px) { .page-heading { align-items: stretch; flex-direction: column; } .page-heading :deep(.el-button) { align-self: flex-start; } }
</style>
