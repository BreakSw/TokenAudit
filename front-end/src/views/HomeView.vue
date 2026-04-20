<template>
  <el-row :gutter="16">
    <el-col :span="16">
      <el-card class="hero-card">
        <div class="hero">
          <div class="hero-left">
            <div class="hero-title">TokenAudit</div>
            <div class="hero-desc">对中转平台 Token 做全维度审计：有效性 / 权限 / 掺水 / 合规 / 稳定性，并输出可追溯证据链报告。</div>
            <div class="hero-actions">
              <el-button type="primary" size="large" @click="$router.push('/audit')">开始审计</el-button>
              <el-button size="large" @click="$router.push('/tokens')">先录入Token</el-button>
            </div>
          </div>
          <div class="hero-right">
            <div class="hero-metric">
              <div class="metric-value">5</div>
              <div class="metric-label">审计维度</div>
            </div>
            <div class="hero-metric">
              <div class="metric-value">多Agent</div>
              <div class="metric-label">流程编排</div>
            </div>
            <div class="hero-metric">
              <div class="metric-value">证据</div>
              <div class="metric-label">可回溯</div>
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
    <el-col :span="8">
      <el-card>
        <div class="side-title">快速开始</div>
        <el-steps direction="vertical" :active="2" class="steps">
          <el-step title="录入Token" description="配置平台/Base URL/宣称模型/非宣称模型" />
          <el-step title="发起审计" description="选择Token与导出格式，一键跑完整流程" />
          <el-step title="查看报告" description="Markdown + 结构化JSON，支持历史追溯" />
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
  </el-row>
</template>

<style scoped>
.hero-card {
  overflow: hidden;
}

.hero {
  display: flex;
  gap: 18px;
  align-items: stretch;
  justify-content: space-between;
}

.hero-left {
  flex: 1;
  min-width: 260px;
}

.hero-title {
  font-size: 26px;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: 0.3px;
}

.hero-desc {
  margin-top: 10px;
  color: rgba(15, 23, 42, 0.68);
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.hero-right {
  width: 240px;
  display: grid;
  gap: 10px;
  align-content: start;
}

.hero-metric {
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.metric-value {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.92);
}

.metric-label {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.6);
}

.side-title {
  font-weight: 800;
  color: rgba(15, 23, 42, 0.88);
  margin-bottom: 10px;
}

.steps {
  padding-right: 8px;
}

@media (max-width: 920px) {
  .hero {
    flex-direction: column;
  }
  .hero-right {
    width: 100%;
    grid-template-columns: 1fr 1fr 1fr;
  }
}
</style>
