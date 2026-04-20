<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <div>
          <div class="card-title">审计报告 #{{ auditId }}</div>
          <div class="card-subtitle">Markdown 可直接复制，JSON 用于结构化取证与二次分析</div>
        </div>
        <div class="actions">
          <el-button @click="reload" :loading="loading">刷新</el-button>
          <el-button type="primary" plain @click="copyMarkdown" :disabled="!markdown">复制Markdown</el-button>
          <el-button @click="$router.push('/history')">返回历史</el-button>
        </div>
      </div>
    </template>

    <div v-if="loading">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else class="content">
      <el-collapse v-model="openGuide">
        <el-collapse-item name="guide" title="新手教程：如何阅读这份报告？">
          <el-alert
            type="info"
            show-icon
            :closable="false"
            title="报告结构"
            description="报告分为：基础信息、5项分维度结果与证据、架构联动说明、综合结论、风险与建议。建议先看“综合结论”，再回到每一项证据核对。"
          />
          <el-alert
            style="margin-top: 10px"
            type="warning"
            show-icon
            :closable="false"
            title="为什么看到“审计中/进度未满”？"
            description="系统是异步审计：报告页会实时显示进度与事件列表，完成后会自动得到完整 Markdown 报告。"
          />
        </el-collapse-item>
      </el-collapse>

      <div class="progress-wrap">
        <div class="progress-head">
          <el-tag :type="statusTagType">{{ statusText }}</el-tag>
          <div style="display: flex; gap: 10px; align-items: center">
            <div class="progress-hint">{{ progressHint }}</div>
            <el-button size="small" @click="refreshOnce" :loading="refreshing">刷新进度</el-button>
          </div>
        </div>
        <el-progress :percentage="progress" :stroke-width="10" />
      </div>

      <el-row :gutter="16">
        <el-col :span="10">
          <div class="summary">
            <div class="summary-title">基础信息</div>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Token(脱敏)">{{ baseInfo?.token_masked || "-" }}</el-descriptions-item>
              <el-descriptions-item label="平台">{{ baseInfo?.platform || "-" }}</el-descriptions-item>
              <el-descriptions-item label="宣称模型">{{ baseInfo?.claimed_model || "-" }}</el-descriptions-item>
              <el-descriptions-item label="审计时间">{{ baseInfo?.audit_time || report?.auditTime || "-" }}</el-descriptions-item>
              <el-descriptions-item label="综合结论">{{ report?.overallConclusion || overall?.overall_conclusion || "-" }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-col>
        <el-col :span="14">
          <div class="summary">
            <div class="summary-title">导出结果</div>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="JSON">{{ exports?.json || "-" }}</el-descriptions-item>
              <el-descriptions-item label="Markdown">{{ exports?.md || "-" }}</el-descriptions-item>
              <el-descriptions-item label="Excel">{{ exports?.xlsx || "-" }}</el-descriptions-item>
              <el-descriptions-item label="PDF">{{ exports?.pdf || "-" }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-col>
      </el-row>

      <el-card v-if="events.length" class="events-card">
        <template #header>
          <div class="card-header">
            <div>
              <div class="card-title">审计过程（事件流）</div>
              <div class="card-subtitle">用于展示真实审计进度与失败定位（token_call / deepseek_call）</div>
            </div>
          </div>
        </template>
        <el-table :data="events.slice(-120)" height="280" stripe style="width: 100%">
          <el-table-column prop="ts" label="时间" width="210" />
          <el-table-column prop="event" label="事件" width="160" />
          <el-table-column label="说明">
            <template #default="{ row }">
              <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ eventText(row) }}</div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-tabs v-model="tab" class="tabs">
        <el-tab-pane label="Markdown" name="md">
          <el-input v-model="markdown" type="textarea" :rows="26" readonly />
        </el-tab-pane>
        <el-tab-pane label="结构化JSON" name="json">
          <el-input v-model="jsonText" type="textarea" :rows="26" readonly />
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-card>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { ElMessage } from "element-plus"
import { getAudit, listAuditEvents } from "../request/api"
import { prettyJson } from "../utils/format"

const props = defineProps({
  auditId: { type: Number, required: true }
})

const loading = ref(false)
const report = ref(null)
const tab = ref("md")
const openGuide = ref(["guide"])
const refreshing = ref(false)
const events = ref([])
let pollTimer = null

const status = computed(() => report.value?.status || "")
const progress = computed(() => Number(report.value?.progress ?? 0))
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
  if (status.value === "completed") return "审计已完成"
  if (status.value === "failed") return "审计失败"
  return ""
})

const baseInfo = computed(() => report.value?.report?.base_info || null)
const overall = computed(() => report.value?.report?.overall || null)
const exports = computed(() => report.value?.report?.exports || null)

const markdown = computed(() => {
  return report.value?.report?.report_markdown || report.value?.report?.reportMarkdown || ""
})
const jsonText = computed(() => prettyJson(report.value || {}))

async function reload() {
  loading.value = true
  try {
    report.value = await getAudit(props.auditId)
    events.value = await listAuditEvents(props.auditId)
    if (report.value?.status === "running") {
      startPolling()
    } else {
      stopPolling()
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "加载失败")
  } finally {
    loading.value = false
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(() => {
    refreshOnce()
  }, 1500)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function refreshOnce() {
  refreshing.value = true
  try {
    report.value = await getAudit(props.auditId)
    events.value = await listAuditEvents(props.auditId)
    if (report.value?.status === "completed" || report.value?.status === "failed") {
      stopPolling()
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "刷新失败")
  } finally {
    refreshing.value = false
  }
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

async function copyMarkdown() {
  if (!markdown.value) return
  try {
    await navigator.clipboard.writeText(markdown.value)
    ElMessage.success("已复制")
  } catch {
    ElMessage.warning("复制失败，请手动选中复制")
  }
}

onMounted(reload)

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
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

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.progress-wrap {
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.progress-hint {
  color: rgba(15, 23, 42, 0.62);
  font-size: 12px;
}

.events-card {
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.summary {
  padding: 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.summary-title {
  font-weight: 800;
  color: rgba(15, 23, 42, 0.86);
  margin-bottom: 10px;
}

.tabs {
  margin-top: 4px;
}
</style>
