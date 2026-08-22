<template>
  <div
    class="product-home"
    :style="{ '--pointer-x': `${pointer.x}%`, '--pointer-y': `${pointer.y}%` }"
    @pointermove="trackPointer"
  >
    <section v-reveal class="home-hero">
      <div class="hero-copy">
        <div class="hero-kicker">
          <span class="live-dot" aria-hidden="true" />
          TOKENAUDIT / TRUST LAYER
        </div>
        <h1>让中转服务的每一次承诺，<span>都有证据可查。</span></h1>
        <p class="hero-lead">
          从可用性、权限边界到模型真实性，TokenAudit 通过真实调用建立可复核的审计证据，而不是只给一个模糊评分。
        </p>
        <div class="hero-actions">
          <button class="primary-action" type="button" @click="router.push('/audit')">
            开始一次审计
            <span aria-hidden="true">→</span>
          </button>
          <button class="quiet-action" type="button" @click="router.push('/')">
            进入控制台
          </button>
        </div>
        <div class="trust-line" aria-label="产品原则">
          <span>真实请求</span>
          <span>凭据脱敏</span>
          <span>证据优先</span>
        </div>
      </div>

      <aside class="route-console" aria-label="中转链路审计示意">
        <div class="console-bar">
          <div>
            <span class="console-dot" />
            LIVE INSPECTION
          </div>
          <span>SESSION / 001</span>
        </div>

        <div class="route-visual">
          <div class="scan-line" aria-hidden="true" />
          <div class="route-node route-node--client">
            <span>01</span>
            <strong>客户端</strong>
            <small>REQUEST</small>
          </div>
          <div class="route-link" aria-hidden="true"><i /></div>
          <div class="route-node route-node--relay">
            <span>02</span>
            <strong>中转网关</strong>
            <small>INSPECTING</small>
          </div>
          <div class="route-link" aria-hidden="true"><i /></div>
          <div class="route-node route-node--model">
            <span>03</span>
            <strong>上游模型</strong>
            <small>RESPONSE</small>
          </div>
        </div>

        <div class="signal-grid">
          <div v-for="signal in signals" :key="signal.label" class="signal-cell">
            <span>{{ signal.label }}</span>
            <strong>{{ signal.value }}</strong>
          </div>
        </div>
        <div class="console-foot">
          <span>从调用事实到审计结论</span>
          <span class="console-ready"><i /> READY</span>
        </div>
      </aside>
    </section>

    <section v-reveal="{ stagger: 80 }" class="scope-strip" aria-label="核心审计范围">
      <div class="scope-intro">
        <span>CORE COVERAGE</span>
        <strong>六个可信维度</strong>
      </div>
      <div v-for="(item, index) in scopes" :key="item" class="scope-item">
        <span>{{ String(index + 1).padStart(2, '0') }}</span>
        {{ item }}
      </div>
    </section>

    <section v-reveal="{ stagger: 120 }" class="evidence-section">
      <div class="section-heading">
        <span class="section-code">01 / EVIDENCE FIRST</span>
        <h2>不是跑分，是一条可复核的证据链</h2>
        <p>每个结论都回到真实请求、状态码、延迟和响应特征，让风险判断有依据，也能被复现。</p>
      </div>
      <div class="evidence-grid">
        <article v-for="(item, index) in evidenceCards" :key="item.title" class="evidence-card">
          <span class="card-index">0{{ index + 1 }}</span>
          <div class="card-symbol" aria-hidden="true">{{ item.symbol }}</div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.detail }}</p>
          <div class="card-foot">{{ item.meta }}</div>
        </article>
      </div>
    </section>

    <section v-reveal="{ stagger: 140 }" class="workflow-section">
      <div class="workflow-nav">
        <div class="section-heading section-heading--compact">
          <span class="section-code">02 / AUDIT PIPELINE</span>
          <h2>一条清晰的审计路径</h2>
          <p>点击步骤，查看 TokenAudit 如何从配置走向可读结论。</p>
        </div>
        <div class="workflow-tabs" role="tablist" aria-label="审计流程">
          <button
            v-for="(step, index) in workflow"
            :key="step.key"
            class="workflow-tab"
            :class="{ 'is-active': activeStep === index }"
            type="button"
            role="tab"
            :aria-selected="activeStep === index"
            :aria-controls="`workflow-panel-${index}`"
            @click="activeStep = index"
          >
            <span>{{ String(index + 1).padStart(2, '0') }}</span>
            <strong>{{ step.label }}</strong>
            <i aria-hidden="true">→</i>
          </button>
        </div>
      </div>

      <div
        :id="`workflow-panel-${activeStep}`"
        class="workflow-panel"
        role="tabpanel"
        aria-live="polite"
      >
        <div class="panel-number">{{ String(activeStep + 1).padStart(2, '0') }}</div>
        <div class="panel-copy">
          <span>{{ currentStep.eyebrow }}</span>
          <h3>{{ currentStep.title }}</h3>
          <p>{{ currentStep.description }}</p>
        </div>
        <div class="panel-checks">
          <div v-for="check in currentStep.checks" :key="check">
            <i aria-hidden="true">✓</i>
            {{ check }}
          </div>
        </div>
      </div>
    </section>

    <section v-reveal="{ stagger: 160 }" class="home-cta">
      <div>
        <span class="section-code">READY WHEN YOU ARE</span>
        <h2>从一枚 Token，开始建立可信判断。</h2>
        <p>录入中转地址与模型信息，审计过程和证据会在控制台中实时呈现。</p>
      </div>
      <div class="cta-actions">
        <button class="primary-action" type="button" @click="router.push('/tokens')">录入 Token</button>
        <button class="quiet-action" type="button" @click="router.push('/guide')">查看使用文档</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const activeStep = ref(0)
const pointer = reactive({ x: 72, y: 16 })

const signals = [
  { label: "PROTOCOL", value: "OPENAI" },
  { label: "AUTH", value: "SCOPED" },
  { label: "EVIDENCE", value: "TRACEABLE" }
]

const scopes = ["接口有效性", "权限边界", "模型真实性", "合规检查", "稳定表现", "安全风险"]

const evidenceCards = [
  {
    symbol: "⌁",
    title: "真实调用",
    detail: "直接请求目标中转接口，记录可用性、状态码与响应耗时。",
    meta: "LIVE API PROBE"
  },
  {
    symbol: "◇",
    title: "多维交叉验证",
    detail: "将权限、模型特征和稳定性分开检查，减少单次回答带来的误判。",
    meta: "MULTI-AGENT REVIEW"
  },
  {
    symbol: "◎",
    title: "可读报告",
    detail: "保留脱敏证据与风险依据，让结论可以复查，也方便后续整改。",
    meta: "AUDITABLE OUTPUT"
  }
]

const workflow = [
  {
    key: "configure",
    label: "配置目标",
    eyebrow: "TARGET CONFIGURATION",
    title: "明确中转地址与宣称能力",
    description: "录入 Token、Base URL 与宣称模型；如需验证模型权限边界，可额外启用目标审计模型。",
    checks: ["敏感凭据脱敏展示", "出站地址安全校验", "审计范围明确可见"]
  },
  {
    key: "probe",
    label: "执行探测",
    eyebrow: "CONTROLLED PROBING",
    title: "用真实请求验证服务行为",
    description: "针对有效性、权限和模型表现发起受控调用，记录客观响应，不使用虚构数据填充结果。",
    checks: ["接口与模型列表探测", "匿名与越权边界检查", "多轮模型能力取样"]
  },
  {
    key: "judge",
    label: "交叉判定",
    eyebrow: "EVIDENCE CORRELATION",
    title: "让事实先于模型结论",
    description: "结构化指标与多 Agent 结果相互印证，AI 负责解释复杂证据，而不是替代客观事实。",
    checks: ["响应特征结构化", "敏感字段再次清洗", "异常与不确定性保留"]
  },
  {
    key: "report",
    label: "生成报告",
    eyebrow: "DECISION OUTPUT",
    title: "把风险变成可执行的判断",
    description: "按审计维度归档结论、证据和整改建议，形成适合复核、分享与导出的完整报告。",
    checks: ["六维结论统一呈现", "风险与建议分层", "JSON / Markdown 多格式"]
  }
]

const currentStep = computed(() => workflow[activeStep.value])

function trackPointer(event) {
  const bounds = event.currentTarget.getBoundingClientRect()
  if (!bounds.width || !bounds.height) return
  pointer.x = ((event.clientX - bounds.left) / bounds.width) * 100
  pointer.y = ((event.clientY - bounds.top) / bounds.height) * 100
}
</script>

<style scoped>
.product-home {
  --home-line: rgba(67, 224, 162, 0.14);
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding-bottom: 18px;
}

.product-home::before {
  position: absolute;
  top: var(--pointer-y);
  left: var(--pointer-x);
  z-index: -1;
  width: 520px;
  height: 520px;
  content: "";
  background: radial-gradient(circle, rgba(67, 224, 162, 0.065), transparent 68%);
  border-radius: 50%;
  pointer-events: none;
  transform: translate(-50%, -50%);
  transition: transform 160ms ease-out;
}

.home-hero {
  position: relative;
  display: grid;
  min-height: 460px;
  grid-template-columns: minmax(0, 0.9fr) minmax(460px, 1.1fr);
  gap: 56px;
  align-items: center;
  padding: 48px;
  overflow: hidden;
  background:
    linear-gradient(115deg, rgba(67, 224, 162, 0.035), transparent 42%),
    var(--ta-panel);
  border: 1px solid var(--ta-line-strong);
  border-radius: 8px;
}

.home-hero::before,
.home-hero::after {
  position: absolute;
  content: "";
  pointer-events: none;
}

.home-hero::before {
  inset: 0;
  background-image:
    linear-gradient(rgba(67, 224, 162, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(67, 224, 162, 0.025) 1px, transparent 1px);
  background-size: 34px 34px;
  mask-image: linear-gradient(90deg, transparent, #000 58%);
}

.home-hero::after {
  top: 0;
  right: 52px;
  width: 140px;
  height: 1px;
  background: var(--ta-green);
  box-shadow: 0 0 18px rgba(67, 224, 162, 0.45);
}

.hero-copy,
.route-console {
  position: relative;
  z-index: 1;
}

.hero-kicker,
.section-code {
  color: var(--ta-green);
  font-family: var(--ta-mono);
  font-size: 10px;
  letter-spacing: 0.13em;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 9px;
}

.live-dot {
  width: 6px;
  height: 6px;
  background: var(--ta-green);
  border-radius: 50%;
  box-shadow: 0 0 0 4px rgba(67, 224, 162, 0.08);
}

.hero-copy h1 {
  max-width: 620px;
  margin: 20px 0 0;
  color: var(--ta-text);
  font-size: clamp(31px, 2.8vw, 40px);
  font-weight: 620;
  letter-spacing: -0.045em;
  line-height: 1.22;
}

.hero-copy h1 span {
  display: block;
  color: rgba(228, 240, 232, 0.54);
  font-weight: 520;
}

.hero-lead {
  max-width: 590px;
  margin: 20px 0 0;
  color: var(--ta-muted);
  font-size: 14px;
  line-height: 1.85;
}

.hero-actions,
.cta-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}

.primary-action,
.quiet-action {
  min-height: 42px;
  padding: 0 17px;
  border-radius: 5px;
  font: inherit;
  font-size: 13px;
  cursor: pointer;
  transition:
    color 180ms ease,
    background 180ms ease,
    border-color 180ms ease,
    transform 180ms ease;
}

.primary-action {
  display: inline-flex;
  align-items: center;
  gap: 28px;
  color: #031009;
  background: var(--ta-green);
  border: 1px solid var(--ta-green);
  font-weight: 650;
}

.primary-action:hover {
  background: #70eaba;
  border-color: #70eaba;
  transform: translateY(-2px);
}

.quiet-action {
  color: var(--ta-muted);
  background: rgba(67, 224, 162, 0.025);
  border: 1px solid var(--ta-line-strong);
}

.quiet-action:hover {
  color: var(--ta-text);
  background: rgba(67, 224, 162, 0.07);
  border-color: rgba(67, 224, 162, 0.34);
}

.trust-line {
  display: flex;
  flex-wrap: wrap;
  gap: 9px 18px;
  margin-top: 30px;
  color: var(--ta-faint);
  font-size: 11px;
}

.trust-line span::before {
  margin-right: 7px;
  color: var(--ta-green);
  content: "+";
  font-family: var(--ta-mono);
}

.route-console {
  padding: 16px;
  background: rgba(3, 6, 4, 0.8);
  border: 1px solid rgba(67, 224, 162, 0.2);
  border-radius: 7px;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34);
}

.console-bar,
.console-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 9px;
  letter-spacing: 0.1em;
}

.console-bar > div,
.console-ready {
  display: flex;
  align-items: center;
  gap: 7px;
}

.console-dot {
  width: 5px;
  height: 5px;
  background: var(--ta-green);
  border-radius: 50%;
}

.route-visual {
  position: relative;
  display: grid;
  min-height: 190px;
  grid-template-columns: 1fr 40px 1fr 40px 1fr;
  align-items: center;
  margin: 16px 0;
  padding: 28px 18px;
  overflow: hidden;
  background:
    linear-gradient(rgba(67, 224, 162, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(67, 224, 162, 0.035) 1px, transparent 1px);
  background-size: 20px 20px;
  border: 1px solid var(--ta-line);
}

.scan-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 80px;
  background: linear-gradient(90deg, transparent, rgba(67, 224, 162, 0.09), transparent);
  animation: route-scan 4.6s ease-in-out infinite;
}

.route-node {
  position: relative;
  z-index: 1;
  display: flex;
  min-height: 94px;
  flex-direction: column;
  justify-content: center;
  padding: 12px;
  background: #07100b;
  border: 1px solid var(--ta-line-strong);
}

.route-node--relay {
  background: rgba(67, 224, 162, 0.09);
  border-color: rgba(67, 224, 162, 0.42);
  box-shadow: 0 0 24px rgba(67, 224, 162, 0.08);
}

.route-node span,
.route-node small {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 8px;
  letter-spacing: 0.08em;
}

.route-node strong {
  margin: 8px 0 6px;
  color: var(--ta-text);
  font-size: 12px;
  font-weight: 620;
}

.route-node--relay small {
  color: var(--ta-green);
}

.route-link {
  position: relative;
  z-index: 1;
  height: 1px;
  overflow: visible;
  background: rgba(67, 224, 162, 0.26);
}

.route-link::after {
  position: absolute;
  top: -3px;
  right: -1px;
  width: 6px;
  height: 6px;
  content: "";
  border-top: 1px solid var(--ta-green);
  border-right: 1px solid var(--ta-green);
  transform: rotate(45deg);
}

.route-link i {
  position: absolute;
  top: -2px;
  left: 0;
  width: 5px;
  height: 5px;
  background: var(--ta-green);
  border-radius: 50%;
  animation: packet 2.4s linear infinite;
}

.signal-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border: 1px solid var(--ta-line);
}

.signal-cell {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 6px;
  padding: 11px;
}

.signal-cell + .signal-cell {
  border-left: 1px solid var(--ta-line);
}

.signal-cell span {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 8px;
  letter-spacing: 0.08em;
}

.signal-cell strong {
  overflow: hidden;
  color: var(--ta-text);
  font-family: var(--ta-mono);
  font-size: 10px;
  font-weight: 500;
  text-overflow: ellipsis;
}

.console-foot {
  margin-top: 14px;
}

.console-ready {
  color: var(--ta-green);
}

.console-ready i {
  width: 5px;
  height: 5px;
  background: var(--ta-green);
  border-radius: 50%;
}

.scope-strip {
  display: grid;
  grid-template-columns: 1.5fr repeat(6, 1fr);
  background: var(--ta-panel);
  border: 1px solid var(--ta-line);
}

.scope-intro,
.scope-item {
  min-height: 72px;
  padding: 15px;
}

.scope-intro {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}

.scope-intro span,
.scope-item span {
  color: var(--ta-green);
  font-family: var(--ta-mono);
  font-size: 8px;
  letter-spacing: 0.1em;
}

.scope-intro strong {
  color: var(--ta-text);
  font-size: 13px;
  font-weight: 620;
}

.scope-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  color: var(--ta-muted);
  border-left: 1px solid var(--ta-line);
  font-size: 11px;
  transition:
    color 180ms ease,
    background 180ms ease;
}

.scope-item:hover {
  color: var(--ta-text);
  background: rgba(67, 224, 162, 0.045);
}

.evidence-section,
.workflow-section {
  padding: 50px 0 10px;
}

.section-heading {
  display: grid;
  max-width: 660px;
  gap: 12px;
}

.section-heading h2,
.home-cta h2 {
  margin: 0;
  color: var(--ta-text);
  font-size: clamp(22px, 2.4vw, 32px);
  font-weight: 620;
  letter-spacing: -0.025em;
  line-height: 1.3;
}

.section-heading p,
.home-cta p {
  margin: 0;
  color: var(--ta-muted);
  font-size: 13px;
  line-height: 1.8;
}

.evidence-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  margin-top: 28px;
  border-top: 1px solid var(--ta-line-strong);
  border-bottom: 1px solid var(--ta-line);
}

.evidence-card {
  position: relative;
  min-height: 256px;
  padding: 25px;
  overflow: hidden;
  background: rgba(10, 18, 14, 0.62);
  transition:
    background 220ms ease,
    transform 220ms ease;
}

.evidence-card + .evidence-card {
  border-left: 1px solid var(--ta-line);
}

.evidence-card:hover {
  z-index: 1;
  background: var(--ta-panel-raised);
  transform: translateY(-4px);
}

.card-index {
  position: absolute;
  top: 24px;
  right: 24px;
  color: var(--ta-decorative);
  font-family: var(--ta-mono);
  font-size: 10px;
}

.card-symbol {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  color: var(--ta-green);
  border: 1px solid var(--ta-line-strong);
  font-size: 18px;
}

.evidence-card h3 {
  margin: 26px 0 0;
  color: var(--ta-text);
  font-size: 17px;
  font-weight: 620;
}

.evidence-card p {
  max-width: 320px;
  margin: 12px 0 0;
  color: var(--ta-muted);
  font-size: 12px;
  line-height: 1.75;
}

.card-foot {
  position: absolute;
  right: 25px;
  bottom: 22px;
  left: 25px;
  padding-top: 12px;
  color: var(--ta-faint);
  border-top: 1px solid var(--ta-line);
  font-family: var(--ta-mono);
  font-size: 8px;
  letter-spacing: 0.1em;
}

.workflow-section {
  display: grid;
  grid-template-columns: minmax(320px, 0.82fr) minmax(0, 1.18fr);
  gap: 48px;
  align-items: end;
}

.section-heading--compact h2 {
  font-size: 26px;
}

.workflow-tabs {
  display: grid;
  margin-top: 26px;
  border-top: 1px solid var(--ta-line);
}

.workflow-tab {
  display: grid;
  min-height: 56px;
  grid-template-columns: 28px 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 0 12px;
  color: var(--ta-muted);
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--ta-line);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    color 180ms ease,
    background 180ms ease;
}

.workflow-tab span {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 9px;
}

.workflow-tab strong {
  font-size: 12px;
  font-weight: 550;
}

.workflow-tab i {
  color: var(--ta-decorative);
  font-style: normal;
  transition: transform 180ms ease;
}

.workflow-tab:hover,
.workflow-tab.is-active {
  color: var(--ta-text);
  background: rgba(67, 224, 162, 0.045);
}

.workflow-tab.is-active span,
.workflow-tab.is-active i {
  color: var(--ta-green);
}

.workflow-tab.is-active i {
  transform: translateX(3px);
}

.workflow-panel {
  position: relative;
  display: grid;
  min-height: 380px;
  align-content: space-between;
  padding: 34px;
  overflow: hidden;
  background:
    linear-gradient(140deg, rgba(67, 224, 162, 0.065), transparent 55%),
    var(--ta-panel);
  border: 1px solid var(--ta-line-strong);
}

.workflow-panel::after {
  position: absolute;
  right: -90px;
  bottom: -140px;
  width: 340px;
  height: 340px;
  content: "";
  border: 1px solid rgba(67, 224, 162, 0.08);
  border-radius: 50%;
  box-shadow:
    0 0 0 42px rgba(67, 224, 162, 0.02),
    0 0 0 84px rgba(67, 224, 162, 0.015);
}

.panel-number {
  position: absolute;
  top: 18px;
  right: 28px;
  color: rgba(67, 224, 162, 0.08);
  font-family: var(--ta-mono);
  font-size: 90px;
  font-weight: 700;
  line-height: 1;
}

.panel-copy,
.panel-checks {
  position: relative;
  z-index: 1;
}

.panel-copy > span {
  color: var(--ta-green);
  font-family: var(--ta-mono);
  font-size: 9px;
  letter-spacing: 0.11em;
}

.panel-copy h3 {
  max-width: 430px;
  margin: 14px 0 0;
  color: var(--ta-text);
  font-size: 24px;
  font-weight: 620;
  letter-spacing: -0.02em;
}

.panel-copy p {
  max-width: 520px;
  margin: 16px 0 0;
  color: var(--ta-muted);
  font-size: 13px;
  line-height: 1.85;
}

.panel-checks {
  display: grid;
  gap: 9px;
  padding-top: 22px;
  border-top: 1px solid var(--ta-line);
}

.panel-checks div {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--ta-muted);
  font-size: 11px;
}

.panel-checks i {
  display: grid;
  width: 17px;
  height: 17px;
  place-items: center;
  color: var(--ta-green);
  border: 1px solid var(--ta-line-strong);
  font-size: 9px;
  font-style: normal;
}

.home-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  margin-top: 52px;
  padding: 34px 38px;
  background: var(--ta-panel);
  border-top: 1px solid var(--ta-line-strong);
  border-bottom: 1px solid var(--ta-line-strong);
}

.home-cta h2 {
  margin-top: 10px;
  font-size: 24px;
}

.home-cta p {
  margin-top: 8px;
}

.home-cta .cta-actions {
  flex: 0 0 auto;
  margin-top: 0;
}

@keyframes route-scan {
  0%, 12% { left: -90px; opacity: 0; }
  25% { opacity: 1; }
  76% { opacity: 1; }
  100% { left: calc(100% + 20px); opacity: 0; }
}

@keyframes packet {
  from { left: 0; }
  to { left: calc(100% - 4px); }
}

@media (max-width: 1120px) {
  .home-hero {
    grid-template-columns: 1fr;
    gap: 38px;
  }

  .route-console {
    max-width: 720px;
  }

  .scope-strip {
    grid-template-columns: repeat(3, 1fr);
  }

  .scope-intro {
    grid-column: 1 / -1;
    border-bottom: 1px solid var(--ta-line);
  }

  .scope-item:nth-child(2),
  .scope-item:nth-child(5) {
    border-left: 0;
  }
}

@media (max-width: 840px) {
  .home-hero {
    min-height: 0;
    padding: 30px 24px;
  }

  .hero-copy h1 {
    font-size: clamp(29px, 8vw, 40px);
  }

  .workflow-section {
    grid-template-columns: 1fr;
  }

  .evidence-grid {
    grid-template-columns: 1fr;
  }

  .evidence-card {
    min-height: 230px;
  }

  .evidence-card + .evidence-card {
    border-top: 1px solid var(--ta-line);
    border-left: 0;
  }

  .home-cta {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 600px) {
  .home-hero {
    padding: 26px 18px;
  }

  .hero-copy h1 {
    font-size: 30px;
  }

  .route-console {
    padding: 11px;
  }

  .route-visual {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 18px;
  }

  .route-link {
    width: 1px;
    height: 20px;
    margin: 0 auto;
  }

  .route-link::after {
    top: auto;
    right: -3px;
    bottom: -1px;
    transform: rotate(135deg);
  }

  .signal-grid {
    grid-template-columns: 1fr;
  }

  .signal-cell + .signal-cell {
    border-top: 1px solid var(--ta-line);
    border-left: 0;
  }

  .scope-strip {
    grid-template-columns: repeat(2, 1fr);
  }

  .scope-item:nth-child(2),
  .scope-item:nth-child(4),
  .scope-item:nth-child(6) {
    border-left: 0;
  }

  .scope-item:nth-child(5) {
    border-left: 1px solid var(--ta-line);
  }

  .workflow-panel {
    min-height: 420px;
    padding: 26px 22px;
  }

  .panel-number {
    font-size: 68px;
  }

  .home-cta {
    margin-top: 34px;
    padding: 26px 20px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .scan-line,
  .route-link i {
    animation: none;
  }

  .product-home::before {
    display: none;
  }

  .primary-action,
  .evidence-card {
    transition: none;
  }
}
</style>
