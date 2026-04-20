<template>
  <div class="landing">
    <el-card class="hero-card">
      <div class="hero">
        <div class="hero-copy">
          <div class="hero-kicker">Token 风险体检平台</div>
          <div class="hero-title">
            更快定位 Token
            <span class="gradient-text">有效性/权限/掺水</span>
            与合规风险
          </div>
          <div class="hero-desc">
            一次点击，自动触发多 Agent 协作审计与 DeepSeek 判定。全程输出真实事件流与证据链，可追溯、可复盘、可导出。
          </div>
          <div class="hero-cta">
            <div class="hero-actions">
              <el-button type="primary" size="large" @click="$router.push('/audit')">开始审计</el-button>
              <el-button size="large" @click="$router.push('/tokens')">先录入Token</el-button>
              <el-button size="large" plain @click="$router.push('/history')">查看历史</el-button>
            </div>
            <div class="hero-badges">
              <div class="badge">实时进度</div>
              <div class="badge">事件流</div>
              <div class="badge">Markdown/JSON/Excel/PDF</div>
            </div>
          </div>
        </div>

        <div class="hero-visual">
          <div class="visual-card">
            <div class="visual-top">
              <div class="visual-title">实时审计面板</div>
              <div class="visual-pill">Live</div>
            </div>
            <div class="visual-progress">
              <div class="visual-progress-head">
                <div class="visual-progress-label">进度</div>
                <div class="visual-progress-value">72%</div>
              </div>
              <el-progress :percentage="72" :stroke-width="10" />
              <div class="visual-phases">
                <div class="phase active">validity</div>
                <div class="phase active">permission</div>
                <div class="phase active">watering</div>
                <div class="phase">compliance</div>
                <div class="phase">stability</div>
                <div class="phase">security</div>
                <div class="phase">overall</div>
              </div>
            </div>

            <div class="mock-card">
              <div class="mock-head">
                <div class="dot red" />
                <div class="dot yellow" />
                <div class="dot green" />
                <div class="mock-title">审计过程（节选）</div>
              </div>
              <div class="mock-body">
                <div class="mock-line"><span class="tag">phase_start</span> validity</div>
                <div class="mock-line"><span class="tag">token_call</span> claude-opus-4-6</div>
                <div class="mock-line"><span class="tag">phase_start</span> permission</div>
                <div class="mock-line"><span class="tag">token_call</span> non-claimed model</div>
                <div class="mock-line"><span class="tag">deepseek_call</span> overall judge</div>
                <div class="mock-line"><span class="tag ok">completed</span> report exported</div>
              </div>
            </div>
          </div>

          <div class="visual-stats">
            <div class="stat-card">
              <div class="stat-value">6</div>
              <div class="stat-label">审计维度</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">多Agent</div>
              <div class="stat-label">调度 + 重试 + 汇总</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">证据链</div>
              <div class="stat-label">可回溯事件与报告</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="8">
        <el-card>
          <div class="feature-title">真实进度</div>
          <div class="feature-desc">后端实时采集 Python stderr 事件流，前端展示阶段、耗时与调用记录。</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="feature-title">可追溯证据</div>
          <div class="feature-desc">每一步都留痕：token_call / deepseek_call / phase_start，报告可复盘。</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="feature-title">面向部署</div>
          <div class="feature-desc">前后端分离，SQLite 轻量存储，.env 配置即可跑通本地与服务器。</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="10">
        <el-card>
          <div class="side-title">快速开始</div>
          <el-steps direction="vertical" :active="2" class="steps">
            <el-step title="录入Token" description="配置平台/Base URL/宣称模型/非宣称模型" />
            <el-step title="发起审计" description="选择Token与导出格式，一键跑完整流程" />
            <el-step title="查看报告" description="Markdown + 结构化JSON + 事件流，支持历史追溯" />
          </el-steps>
          <el-alert
            style="margin-top: 12px"
            type="info"
            show-icon
            :closable="false"
            title="提示"
            description="Token Base URL 填域名根，例如 https://xxx.com（系统会自动请求 /v1/chat/completions）"
          />
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card class="guide-card">
          <div class="guide-title">你会得到什么</div>
          <div class="guide-grid">
            <div class="guide-item">
              <div class="guide-k">异常定位</div>
              <div class="guide-v">失败时可按事件定位到具体阶段与请求</div>
            </div>
            <div class="guide-item">
              <div class="guide-k">越权检测</div>
              <div class="guide-v">对比宣称模型/非宣称模型/匿名调用</div>
            </div>
            <div class="guide-item">
              <div class="guide-k">稳定性画像</div>
              <div class="guide-v">多次调用一致性与波动分析</div>
            </div>
            <div class="guide-item">
              <div class="guide-k">导出归档</div>
              <div class="guide-v">JSON/Markdown/Excel/PDF，便于审计留存</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.landing {
  display: flex;
  flex-direction: column;
}

.hero-card {
  overflow: hidden;
}

.hero {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  gap: 18px;
  align-items: stretch;
  justify-content: space-between;
}

.hero-copy {
  min-width: 260px;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  color: rgba(37, 99, 235, 0.92);
  background: rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(37, 99, 235, 0.18);
}

.hero-title {
  margin-top: 10px;
  font-size: 30px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: 0.3px;
  line-height: 1.15;
}

.hero-desc {
  margin-top: 10px;
  color: rgba(15, 23, 42, 0.68);
  line-height: 1.6;
}

.hero-cta {
  margin-top: 18px;
  width: fit-content;
  padding: 10px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(17, 24, 39, 0.08);
  box-shadow: 0 18px 50px rgba(17, 24, 39, 0.08);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-actions :deep(.el-button) {
  height: 40px;
  border-radius: 12px;
}

.hero-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  font-size: 12px;
  font-weight: 700;
  color: rgba(15, 23, 42, 0.7);
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 999px;
  padding: 6px 10px;
}

.hero-visual {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 320px;
}

.visual-card {
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(17, 24, 39, 0.08);
  box-shadow: 0 18px 50px rgba(17, 24, 39, 0.08);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.visual-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.visual-title {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
}

.visual-pill {
  height: 28px;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  color: rgba(16, 185, 129, 0.92);
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.18);
}

.visual-progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.visual-progress-label {
  font-size: 12px;
  font-weight: 800;
  color: rgba(15, 23, 42, 0.66);
}

.visual-progress-value {
  font-size: 12px;
  font-weight: 900;
  color: rgba(15, 23, 42, 0.78);
}

.visual-phases {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.phase {
  font-size: 12px;
  font-weight: 800;
  color: rgba(15, 23, 42, 0.62);
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 999px;
  padding: 6px 10px;
}

.phase.active {
  color: rgba(37, 99, 235, 0.92);
  background: rgba(37, 99, 235, 0.12);
  border: 1px solid rgba(37, 99, 235, 0.18);
}

.visual-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.stat-card {
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.stat-value {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
}

.stat-label {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.6);
}

.mock-card {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.mock-head {
  height: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.06);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
}

.dot.red {
  background: #ef4444;
}

.dot.yellow {
  background: #f59e0b;
}

.dot.green {
  background: #10b981;
}

.mock-title {
  margin-left: 6px;
  color: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  font-weight: 700;
}

.mock-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-family:
    ui-monospace,
    SFMono-Regular,
    Menlo,
    Monaco,
    Consolas,
    "Liberation Mono",
    "Courier New",
    monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
}

.mock-line {
  display: flex;
  gap: 8px;
  align-items: center;
}

.tag {
  display: inline-flex;
  align-items: center;
  height: 20px;
  padding: 0 8px;
  border-radius: 999px;
  font-weight: 800;
  background: rgba(37, 99, 235, 0.22);
  color: rgba(255, 255, 255, 0.92);
}

.tag.ok {
  background: rgba(16, 185, 129, 0.25);
}

.feature-title {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.9);
}

.feature-desc {
  margin-top: 8px;
  color: rgba(15, 23, 42, 0.62);
  line-height: 1.6;
}

.side-title {
  font-weight: 800;
  color: rgba(15, 23, 42, 0.88);
  margin-bottom: 10px;
}

.steps {
  padding-right: 8px;
}

.guide-card {
  overflow: hidden;
}

.guide-title {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
  margin-bottom: 12px;
}

.guide-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.guide-item {
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.guide-k {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
}

.guide-v {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.62);
  line-height: 1.6;
}

@media (max-width: 920px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .hero-cta {
    width: 100%;
  }
  .hero-actions {
    width: 100%;
  }
  .hero-actions :deep(.el-button) {
    flex: 1;
  }
  .hero-visual {
    min-width: auto;
  }
  .visual-stats {
    grid-template-columns: 1fr;
  }
  .guide-grid {
    grid-template-columns: 1fr;
  }
}
</style>
