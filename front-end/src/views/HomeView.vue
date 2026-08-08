<template>
  <main class="dashboard">
    <header v-reveal class="dashboard-header">
      <div>
        <p class="eyebrow">OPERATIONS / TOKEN AUDIT</p>
        <h1>审计控制台</h1>
        <p class="dashboard-description">集中查看 Token 资产、审计任务和执行状态。</p>
      </div>
      <div class="update-time">
        <span class="status-dot" />
        <span>{{ updatedAt ? `数据更新于 ${updatedAt}` : loading ? "正在同步数据" : "数据暂不可用" }}</span>
      </div>
    </header>

    <section v-if="loading" v-reveal class="state-panel" aria-live="polite">
      <span class="state-code">LOADING</span>
      <div>
        <h2>正在加载审计数据</h2>
        <p>正在同步 Token 与审计任务，请稍候。</p>
      </div>
    </section>

    <section v-else-if="error" v-reveal class="state-panel state-panel--error" role="alert">
      <span class="state-code">ERROR</span>
      <div>
        <h2>仪表盘数据加载失败</h2>
        <p>{{ error }}</p>
        <el-button type="primary" @click="loadDashboard">重新加载</el-button>
      </div>
    </section>

    <template v-else-if="dashboardData">
      <section v-reveal class="metrics" aria-label="审计指标">
        <article
          v-for="(metric, index) in metrics"
          :key="metric.label"
          v-reveal="{ stagger: index * 45 }"
          class="metric-card"
          :class="metric.tone"
        >
          <div class="metric-head">
            <span>{{ metric.label }}</span>
            <span class="metric-key">{{ metric.key }}</span>
          </div>
          <strong>{{ metric.value }}</strong>
          <p>{{ metric.detail }}</p>
        </article>
      </section>

      <section
        v-if="dashboardData.tokenCount === 0 && dashboardData.auditCount === 0"
        v-reveal="{ stagger: 80 }"
        class="empty-banner"
      >
        <div>
          <span class="state-code">EMPTY</span>
          <h2>当前没有可展示的审计数据</h2>
          <p>先录入 Token，再发起第一项审计任务。</p>
        </div>
        <el-button type="primary" @click="router.push('/tokens')">录入 Token</el-button>
      </section>

      <section v-reveal="{ stagger: 100 }" class="workspace-grid">
        <article class="panel recent-panel">
          <div class="panel-header">
            <div>
              <span class="section-index">01 / RECENT</span>
              <h2>最近审计任务</h2>
            </div>
            <el-button text @click="router.push('/history')">全部历史 →</el-button>
          </div>

          <div v-if="dashboardData.latestAudit" class="audit-record">
            <div class="audit-record__top">
              <div>
                <span class="record-label">AUDIT ID</span>
                <strong>#{{ dashboardData.latestAudit.id }}</strong>
              </div>
              <el-tag :type="statusType(dashboardData.latestAudit.status)" effect="plain">
                {{ dashboardData.latestAudit.status || "unknown" }}
              </el-tag>
            </div>
            <dl class="record-grid">
              <div>
                <dt>审计时间</dt>
                <dd>{{ dashboardData.latestAudit.auditTime || "未记录" }}</dd>
              </div>
              <div>
                <dt>Token ID</dt>
                <dd>{{ dashboardData.latestAudit.tokenId ?? "未记录" }}</dd>
              </div>
              <div class="record-grid__wide">
                <dt>综合结论</dt>
                <dd>
                  {{
                    dashboardData.latestAudit.overallConclusion ||
                    dashboardData.latestAudit.conclusion ||
                    "暂无综合结论"
                  }}
                </dd>
              </div>
            </dl>
            <el-button
              v-if="dashboardData.latestAudit.id != null"
              type="primary"
              @click="router.push(`/report/${dashboardData.latestAudit.id}`)"
            >
              查看审计报告
            </el-button>
          </div>

          <div v-else class="panel-empty">
            <span class="state-code">NO AUDITS</span>
            <h3>暂无审计任务</h3>
            <p>选择已录入的 Token 发起审计，执行记录会显示在这里。</p>
            <el-button type="primary" @click="router.push('/audit')">发起审计</el-button>
          </div>
        </article>

        <aside class="panel quick-panel">
          <div class="panel-header">
            <div>
              <span class="section-index">02 / ACTIONS</span>
              <h2>快速操作</h2>
            </div>
          </div>
          <button class="action-link" type="button" @click="router.push('/audit')">
            <span>
              <strong>发起审计</strong>
              <small>选择 Token 并执行完整审计流程</small>
            </span>
            <span aria-hidden="true">→</span>
          </button>
          <button class="action-link" type="button" @click="router.push('/tokens')">
            <span>
              <strong>管理 Token</strong>
              <small>录入、检查或移除 Token 资产</small>
            </span>
            <span aria-hidden="true">→</span>
          </button>
        </aside>
      </section>

      <section v-reveal="{ stagger: 140 }" class="panel stages-panel">
        <div class="panel-header">
          <div>
            <span class="section-index">03 / COVERAGE</span>
            <h2>审计维度</h2>
          </div>
          <span class="panel-note">6 个检查阶段</span>
        </div>
        <div class="stage-list">
          <article v-for="(stage, index) in auditDimensions" :key="stage.key" class="stage-row">
            <span class="stage-number">{{ String(index + 1).padStart(2, "0") }}</span>
            <div class="stage-copy">
              <strong>{{ stage.label }}</strong>
              <p>{{ stage.detail }}</p>
            </div>
            <code>{{ stage.key }}</code>
          </article>
        </div>
      </section>
    </template>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { AUDIT_STAGES } from "../constants/auditStages"
import { listAudits, listTokens } from "../request/api"
import { summarizeDashboard } from "../utils/dashboard"

const router = useRouter()
const loading = ref(true)
const error = ref("")
const updatedAt = ref("")
const dashboardData = ref(null)

const auditDimensions = AUDIT_STAGES.filter((stage) => stage.key !== "overall")

const metrics = computed(() => {
  if (!dashboardData.value) return []

  return [
    {
      label: "Token 数",
      key: "TOKENS",
      value: dashboardData.value.tokenCount,
      detail: "当前已录入资产",
      tone: ""
    },
    {
      label: "审计任务",
      key: "AUDITS",
      value: dashboardData.value.auditCount,
      detail: "累计任务总数",
      tone: ""
    },
    {
      label: "运行中",
      key: "RUNNING",
      value: dashboardData.value.runningCount,
      detail: "正在执行的任务",
      tone: "metric-card--running"
    },
    {
      label: "失败任务",
      key: "FAILED",
      value: dashboardData.value.failedCount,
      detail: "需要排查的任务",
      tone: "metric-card--failed"
    }
  ]
})

async function loadDashboard() {
  loading.value = true
  error.value = ""
  dashboardData.value = null
  updatedAt.value = ""

  try {
    const [tokens, audits] = await Promise.all([listTokens(), listAudits()])
    dashboardData.value = summarizeDashboard(tokens, audits)
    updatedAt.value = new Date().toLocaleString("zh-CN", { hour12: false })
  } catch (cause) {
    const detail = cause?.response?.data?.error || cause?.message
    error.value = detail ? `无法从服务端获取真实数据：${detail}` : "无法从服务端获取真实数据，请检查连接后重试。"
  } finally {
    loading.value = false
  }
}

function statusType(status) {
  if (status === "completed") return "success"
  if (status === "running") return "warning"
  if (status === "failed") return "danger"
  return "info"
}

onMounted(loadDashboard)
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dashboard-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--ta-line);
}

.eyebrow,
.section-index,
.state-code,
.metric-key,
.record-label,
.stage-number,
.stage-row code {
  font-family: var(--ta-mono);
  letter-spacing: 0.08em;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--ta-green);
  font-size: 11px;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 5px;
  color: var(--ta-text);
  font-size: clamp(24px, 3vw, 32px);
  line-height: 1.15;
}

.dashboard-description {
  margin-bottom: 0;
  color: var(--ta-muted);
  font-size: 13px;
}

.update-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 11px;
  white-space: nowrap;
}

.status-dot {
  width: 7px;
  height: 7px;
  background: var(--ta-green);
  border-radius: 50%;
}

.state-panel,
.empty-banner {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  padding: 22px;
  color: var(--ta-text);
  background: var(--ta-panel);
  border: 1px solid var(--ta-line);
  border-radius: var(--ta-radius);
}

.state-panel--error {
  border-color: var(--ta-danger);
}

.state-code {
  flex: 0 0 auto;
  padding: 4px 6px;
  color: var(--ta-green);
  background: var(--ta-code);
  border: 1px solid var(--ta-line-strong);
  border-radius: 4px;
  font-size: 10px;
}

.state-panel--error .state-code,
.metric-card--failed .metric-key {
  color: var(--ta-danger);
}

.state-panel h2,
.empty-banner h2 {
  margin-bottom: 6px;
  font-size: 17px;
}

.state-panel p,
.empty-banner p,
.panel-empty p {
  margin-bottom: 14px;
  color: var(--ta-muted);
  line-height: 1.6;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.metric-card {
  min-width: 0;
  padding: 15px;
  background: var(--ta-panel);
  border: 1px solid var(--ta-line);
  border-radius: var(--ta-radius);
}

.metric-card--running {
  border-color: var(--ta-line-strong);
}

.metric-card--failed {
  border-color: var(--ta-line-strong);
}

.metric-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--ta-muted);
  font-size: 12px;
}

.metric-key {
  color: var(--ta-faint);
  font-size: 9px;
}

.metric-card--running .metric-key {
  color: var(--ta-amber);
}

.metric-card strong {
  display: block;
  margin-top: 12px;
  color: var(--ta-text);
  font-family: var(--ta-mono);
  font-size: 30px;
  line-height: 1;
}

.metric-card p {
  margin: 8px 0 0;
  color: var(--ta-faint);
  font-size: 11px;
}

.empty-banner {
  align-items: center;
  justify-content: space-between;
}

.empty-banner .state-code {
  display: inline-block;
  margin-bottom: 10px;
}

.empty-banner p {
  margin-bottom: 0;
}

.workspace-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(260px, 1fr);
  gap: 12px;
}

.panel {
  min-width: 0;
  padding: 18px;
  background: var(--ta-panel);
  border: 1px solid var(--ta-line);
  border-radius: var(--ta-radius);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 13px;
  border-bottom: 1px solid var(--ta-line);
}

.section-index {
  display: block;
  margin-bottom: 5px;
  color: var(--ta-green);
  font-size: 9px;
}

.panel-header h2 {
  margin-bottom: 0;
  color: var(--ta-text);
  font-size: 17px;
}

.panel-note {
  color: var(--ta-faint);
  font-size: 11px;
}

.audit-record {
  padding: 15px;
  background: var(--ta-panel-raised);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
}

.audit-record__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.record-label {
  display: block;
  margin-bottom: 4px;
  color: var(--ta-faint);
  font-size: 9px;
}

.audit-record__top strong {
  color: var(--ta-text);
  font-family: var(--ta-mono);
  font-size: 21px;
}

.record-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin: 18px 0;
}

.record-grid div {
  min-width: 0;
}

.record-grid__wide {
  grid-column: 1 / -1;
  padding-top: 12px;
  border-top: 1px solid var(--ta-line);
}

.record-grid dt {
  margin-bottom: 5px;
  color: var(--ta-faint);
  font-size: 11px;
}

.record-grid dd {
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--ta-muted);
  line-height: 1.5;
}

.panel-empty {
  padding: 24px 8px 8px;
  text-align: center;
}

.panel-empty h3 {
  margin: 12px 0 6px;
  color: var(--ta-text);
}

.quick-panel {
  display: flex;
  flex-direction: column;
}

.action-link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  padding: 14px 12px;
  color: var(--ta-text);
  text-align: left;
  background: var(--ta-panel-raised);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
  cursor: pointer;
}

.action-link + .action-link {
  margin-top: 10px;
}

.action-link:hover,
.action-link:focus-visible {
  border-color: var(--ta-green);
}

.action-link strong,
.action-link small {
  display: block;
}

.action-link small {
  margin-top: 5px;
  color: var(--ta-faint);
  line-height: 1.4;
}

.action-link > span:last-child {
  color: var(--ta-green);
  font-family: var(--ta-mono);
}

.stage-list {
  border-top: 1px solid var(--ta-line);
}

.stage-row {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr) minmax(110px, auto);
  align-items: center;
  gap: 16px;
  min-height: 66px;
  padding: 10px 4px;
  border-bottom: 1px solid var(--ta-line);
}

.stage-number {
  color: var(--ta-decorative);
  font-size: 11px;
}

.stage-copy strong {
  color: var(--ta-text);
}

.stage-copy p {
  margin: 4px 0 0;
  color: var(--ta-muted);
  font-size: 12px;
}

.stage-row code {
  justify-self: end;
  padding: 4px 6px;
  color: var(--ta-green);
  background: var(--ta-code);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
  font-size: 10px;
}

@media (max-width: 900px) {
  .metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .dashboard-header,
  .empty-banner {
    align-items: flex-start;
    flex-direction: column;
  }

  .metrics {
    grid-template-columns: 1fr;
  }

  .state-panel {
    flex-direction: column;
  }

  .record-grid {
    grid-template-columns: 1fr;
  }

  .record-grid__wide {
    grid-column: auto;
  }

  .stage-row {
    grid-template-columns: 28px minmax(0, 1fr);
    gap: 10px;
  }

  .stage-row code {
    grid-column: 2;
    justify-self: start;
  }
}
</style>
