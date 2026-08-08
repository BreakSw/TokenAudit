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
          <el-button type="primary" size="small" @click="router.push('/audit')">发起审计</el-button>
        </div>
      </div>

      <div v-else data-testid="history-table" class="table-scroll" tabindex="0" aria-label="审计历史列表，可横向滚动">
        <el-table :data="records" class="compact-table" style="width: 100%">
          <el-table-column label="审计 ID" width="94">
            <template #default="{ row }"><code class="mono-value">#{{ row.id }}</code></template>
          </el-table-column>
          <el-table-column label="Token ID" width="100">
            <template #default="{ row }"><code class="mono-value">{{ row.tokenId }}</code></template>
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
          <el-table-column label="操作" width="108">
            <template #default="{ row }">
              <el-button type="primary" plain size="small" @click="open(row.id)">查看报告</el-button>
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
import { ElMessage } from "element-plus"
import { listAudits } from "../request/api"

const router = useRouter()
const records = ref([])
const loading = ref(true)
const loadError = ref("")
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
  router.push(`/report/${id}`)
}

function statusType(status) {
  if (status === "completed") return "success"
  if (status === "running") return "warning"
  if (status === "failed") return "danger"
  return "info"
}

onMounted(reload)
onBeforeUnmount(() => {
  componentAlive = false
  requestSequence += 1
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
.compact-table { min-width: 982px; }
.compact-table :deep(.el-table__cell) { padding: 8px 0; }
.compact-table :deep(.cell) { font-size: 11px; }
.mono-value { color: var(--ta-green); font-size: 10px; }
.status-badge { font-family: var(--ta-mono); font-size: 9px; text-transform: uppercase; }
.status-badge--completed { color: var(--ta-green); }
.status-badge--running { color: var(--ta-amber); }
.status-badge--failed { color: var(--ta-danger); }
.progress-cell { display: grid; grid-template-columns: minmax(55px, 1fr) 34px; gap: 7px; align-items: center; }
.progress-cell span { color: var(--ta-muted); font-size: 9px; text-align: right; }
.conclusion-text { display: block; overflow: hidden; color: var(--ta-muted); text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 600px) { .page-heading { align-items: stretch; flex-direction: column; } .page-heading :deep(.el-button) { align-self: flex-start; } }
</style>
