<template>
  <div class="docs-page">
    <header class="docs-search">
      <label for="guide-search">搜索文档</label>
      <div class="search-control">
        <span aria-hidden="true">⌕</span>
        <input
          id="guide-search"
          v-model="query"
          data-testid="guide-search"
          type="search"
          placeholder="搜索章节、端点或错误码"
          autocomplete="off"
        />
      </div>
    </header>

    <div class="docs-layout">
      <aside class="guide-sidebar">
        <nav aria-label="文档导航">
          <template v-for="group in filteredGroups" :key="group.label">
            <div v-if="group.items.length" class="nav-group">
              <p>{{ group.label }}</p>
              <a v-for="item in group.items" :key="item.id" :href="`#${item.id}`">
                {{ item.title }}
              </a>
            </div>
          </template>
          <p v-if="filteredSections.length === 0" class="nav-empty" role="status">
            没有匹配的章节
          </p>
        </nav>
      </aside>

      <article class="guide-article" data-testid="guide-article">
        <div class="article-heading">
          <p class="eyebrow">TOKENAUDIT / QUICKSTART</p>
          <h1>API 使用指南</h1>
          <p>
            从本地环境到审计报告的最短路径。示例基于当前仓库接口，后端默认运行在
            <code>http://localhost:8086</code>。
          </p>
        </div>

        <section id="requirements" v-reveal>
          <h2><a href="#requirements">运行要求</a></h2>
          <p>
            准备 Node.js 与 npm、Java 与 Maven，以及 Python 3。前端与 API 是常驻服务；审计核心由 API 在收到任务后拉起。
          </p>
          <dl class="requirements-list">
            <div><dt>前端</dt><dd>Vue 3 + Vite，开发端口 <code>5173</code></dd></div>
            <div><dt>后端</dt><dd>Spring Boot，API 端口 <code>8086</code></dd></div>
            <div><dt>审计核心</dt><dd>Python 模块 <code>audit_core</code></dd></div>
          </dl>
        </section>

        <section id="configure" v-reveal>
          <h2><a href="#configure">配置环境变量</a></h2>
          <p>
            在仓库根目录创建或修改 <code>.env</code>，供 Spring 后端和 Python 审计核心读取。
            <code>DEEPSEEK_API_KEY</code> 用于审计判定；<code>BACKEND_API_KEY</code> 留空时不启用后端访问密钥。
          </p>
          <div class="code-shell" data-testid="copy-environment">
            <div class="code-toolbar">
              <span>.env（仓库根目录）</span>
              <button
                type="button"
                aria-label="复制后端环境变量示例"
                @click="copyCode('environment', codeSamples.environment)"
              >复制</button>
              <span
                v-if="copyState.environment"
                class="copy-feedback"
                :role="copyState.environment.role"
                aria-live="polite"
              >{{ copyState.environment.message }}</span>
            </div>
            <pre><code>{{ codeSamples.environment }}</code></pre>
          </div>
          <p>
            Vite 默认不会读取仓库根目录的 <code>.env</code>。请将前端变量写入
            <code>front-end/.env.development</code>，也可在启动 Vite 前通过进程环境设置。
          </p>
          <div class="code-shell" data-testid="copy-frontend-environment">
            <div class="code-toolbar">
              <span>front-end/.env.development</span>
              <button
                type="button"
                aria-label="复制前端环境变量示例"
                @click="copyCode('frontEnvironment', codeSamples.frontEnvironment)"
              >复制</button>
              <span
                v-if="copyState.frontEnvironment"
                class="copy-feedback"
                :role="copyState.frontEnvironment.role"
                aria-live="polite"
              >{{ copyState.frontEnvironment.message }}</span>
            </div>
            <pre><code>{{ codeSamples.frontEnvironment }}</code></pre>
          </div>
          <p data-testid="api-key-rule">
            <code>BACKEND_API_KEY</code> 未启用时可省略 <code>X-API-KEY</code>；启用后每个 API 请求必须携带
            <code>X-API-KEY</code>（浏览器的 <code>OPTIONS</code> 预检除外）。应用设置页保存密钥后会自动添加该请求头。
          </p>
        </section>

        <section id="start" v-reveal>
          <h2><a href="#start">启动项目</a></h2>
          <p>
            先安装 Python 依赖，然后只需启动 Spring Boot 后端和 Vite 前端。无需单独启动审计核心；
            后端按任务执行 <code>python -m audit_core</code>，向其 stdin 写入一次 JSON，进程输出报告后退出。
          </p>
          <div class="code-shell" data-testid="copy-start">
            <div class="code-toolbar">
              <span>powershell / bash</span>
              <button
                type="button"
                aria-label="复制安装与启动命令示例"
                @click="copyCode('start', codeSamples.start)"
              >复制</button>
              <span
                v-if="copyState.start"
                class="copy-feedback"
                :role="copyState.start.role"
                aria-live="polite"
              >{{ copyState.start.message }}</span>
            </div>
            <pre><code>{{ codeSamples.start }}</code></pre>
          </div>

          <h3 id="health">检查 Agent 健康状态</h3>
          <div class="endpoint-block" data-testid="copy-health">
            <div class="endpoint-heading">
              <span class="method method--get">GET</span>{{ " " }}<code>/api/agents/health</code>
              <button
                type="button"
                aria-label="复制健康检查示例"
                @click="copyCode('health', codeSamples.health)"
              >复制</button>
              <span
                v-if="copyState.health"
                class="copy-feedback"
                :role="copyState.health.role"
                aria-live="polite"
              >{{ copyState.health.message }}</span>
            </div>
            <pre><code>{{ codeSamples.health }}</code></pre>
          </div>
        </section>

        <section id="token" v-reveal>
          <h2><a href="#token">录入 Token</a></h2>
          <p>
            可在“Token 管理”页面录入，也可调用 <code>POST /api/tokens</code>。Base URL 只填写服务根地址，
            不要包含 <code>/v1/chat/completions</code>。接口返回掩码后的 <code>tokenMasked</code>，不会回传明文。
          </p>
          <div class="code-shell" data-testid="copy-token">
            <div class="code-toolbar">
              <span>request</span>
              <button
                type="button"
                aria-label="复制创建 Token 示例"
                @click="copyCode('token', codeSamples.token)"
              >复制</button>
              <span
                v-if="copyState.token"
                class="copy-feedback"
                :role="copyState.token.role"
                aria-live="polite"
              >{{ copyState.token.message }}</span>
            </div>
            <pre><code>{{ codeSamples.token }}</code></pre>
          </div>
        </section>

        <section id="run-audit" v-reveal>
          <h2><a href="#run-audit">发起审计</a></h2>
          <p>
            审计覆盖六个维度：<strong>有效性</strong>、<strong>权限</strong>、<strong>模型真实性</strong>、
            <strong>合规</strong>、<strong>稳定性</strong>、<strong>安全性</strong>。未传
            <code>auditDimensions</code> 时审计核心默认运行全部六项。
          </p>
          <div class="endpoint-block" data-testid="copy-audit">
            <div class="endpoint-heading">
              <span class="method method--post">POST</span>{{ " " }}<code>/api/audits</code>
              <button
                type="button"
                aria-label="复制创建审计示例"
                @click="copyCode('audit', codeSamples.audit)"
              >复制</button>
              <span
                v-if="copyState.audit"
                class="copy-feedback"
                :role="copyState.audit.role"
                aria-live="polite"
              >{{ copyState.audit.message }}</span>
            </div>
            <pre><code>{{ codeSamples.audit }}</code></pre>
          </div>

          <h3 id="events">读取实时事件</h3>
          <p>
            <code>POST /api/audits</code> 异步返回 <code>auditId</code>。使用事件接口轮询真实进度；事件对象包含
            <code>id</code>、<code>ts</code>、<code>event</code> 与 <code>payload</code>。
          </p>
          <div class="endpoint-block" data-testid="copy-events">
            <div class="endpoint-heading">
              <span class="method method--get">GET</span>{{ " " }}<code>/api/audits/{id}/events</code>
              <button
                type="button"
                aria-label="复制审计事件示例"
                @click="copyCode('events', codeSamples.events)"
              >复制</button>
              <span
                v-if="copyState.events"
                class="copy-feedback"
                :role="copyState.events.role"
                aria-live="polite"
              >{{ copyState.events.message }}</span>
            </div>
            <pre><code>{{ codeSamples.events }}</code></pre>
          </div>
        </section>

        <section id="report" v-reveal>
          <h2><a href="#report">查看报告</a></h2>
          <p>
            查询接口返回 <code>status</code>、<code>progress</code> 与 <code>report</code>。状态为
            <code>completed</code> 后，可在报告页阅读 Markdown/JSON 结果；导出文件写入配置的报告目录。
          </p>
          <div class="endpoint-block" data-testid="copy-report">
            <div class="endpoint-heading">
              <span class="method method--get">GET</span>{{ " " }}<code>/api/audits/{id}</code>
              <button
                type="button"
                aria-label="复制审计报告示例"
                @click="copyCode('report', codeSamples.report)"
              >复制</button>
              <span
                v-if="copyState.report"
                class="copy-feedback"
                :role="copyState.report.role"
                aria-live="polite"
              >{{ copyState.report.message }}</span>
            </div>
            <pre><code>{{ codeSamples.report }}</code></pre>
          </div>
        </section>

        <section id="errors" v-reveal>
          <h2><a href="#errors">常见错误</a></h2>
          <div class="error-row">
            <code>401 / 403</code>
            <p>确认后端是否设置了 <code>BACKEND_API_KEY</code>，并让 <code>X-API-KEY</code> 与其一致。</p>
          </div>
          <div class="error-row">
            <code>Model Not Exist</code>
            <p>检查 <code>DEEPSEEK_MODEL</code> 是否为当前账号可用模型，修改后重启后端。</p>
          </div>
          <div class="error-row">
            <code>Cannot run program "python"</code>
            <p>确认 Python 位于 PATH，或通过 <code>PYTHON_EXECUTABLE</code> 指定可执行文件。</p>
          </div>
          <div class="error-row">
            <code>503 / audit_failed</code>
            <p>先读取事件接口中的 <code>audit_failed</code> payload，再检查目标模型服务与 DeepSeek 配置。</p>
          </div>
        </section>
      </article>

      <aside class="toc-sidebar">
        <nav aria-label="本页目录">
          <p>本页目录</p>
          <a v-for="item in tableOfContents" :key="item.id" :href="`#${item.id}`">
            {{ item.title }}
          </a>
        </nav>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from "vue"

import { GUIDE_SECTIONS, searchGuideSections } from "../content/guide"

const query = ref("")
const copyState = reactive({})

const navigationGroups = [
  { label: "开始", ids: ["requirements", "configure", "start"] },
  { label: "工作流", ids: ["token", "run-audit", "report"] },
  { label: "参考", ids: ["errors"] }
]

const tableOfContents = [
  { id: "requirements", title: "运行要求" },
  { id: "configure", title: "配置环境变量" },
  { id: "start", title: "启动项目" },
  { id: "token", title: "录入 Token" },
  { id: "run-audit", title: "发起审计" },
  { id: "events", title: "读取实时事件" },
  { id: "report", title: "查看报告" },
  { id: "errors", title: "常见错误" }
]

const codeSamples = {
  environment: `DEEPSEEK_API_KEY=<your-deepseek-key>
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
BACKEND_API_KEY=`,
  frontEnvironment: `VITE_BACKEND_BASE_URL=http://localhost:8086`,
  start: `# 安装步骤：在仓库根目录执行一次
cd audit-core
pip install -r requirements.txt
cd ..

# 运行服务：终端 1 启动 Spring Boot API（http://localhost:8086）
cd back-end
mvn spring-boot:run

# 运行服务：终端 2 启动 Vite（http://localhost:5173）
cd front-end
npm install
npm run dev`,
  health: `# GET /api/agents/health
# BACKEND_API_KEY 未启用时可删除 -H 参数
curl http://localhost:8086/api/agents/health -H "X-API-KEY: <backend-key>"

HTTP/1.1 200 OK
Content-Type: application/json

{"status":"ok"}`,
  token: `# POST /api/tokens；BACKEND_API_KEY 未启用时可删除 X-API-KEY 请求头
curl --request POST http://localhost:8086/api/tokens \\
  --header "Content-Type: application/json" \\
  --header "X-API-KEY: <backend-key>" \\
  --data '{"name":"production-relay","token":"sk-...","platform":"relay","tokenBaseUrl":"https://api.example.com","claimedModel":"claude-opus-4-6","nonClaimedModel":"gpt-4o-mini"}'`,
  audit: `# POST /api/audits；BACKEND_API_KEY 未启用时可删除 X-API-KEY 请求头
curl --request POST http://localhost:8086/api/audits \\
  --header "Content-Type: application/json" \\
  --header "X-API-KEY: <backend-key>" \\
  --data '{"tokenId":12,"exportFormats":["json","md"],"auditDimensions":["validity","permission","watering","compliance","stability","security"]}'

HTTP/1.1 200 OK
{"auditId":42,"report":null}`,
  events: `# GET /api/audits/{id}/events
# BACKEND_API_KEY 未启用时可删除 -H 参数
curl http://localhost:8086/api/audits/42/events -H "X-API-KEY: <backend-key>"

HTTP/1.1 200 OK
[
  {
    "id": 301,
    "ts": "2026-08-08T06:00:00Z",
    "event": "phase_start",
    "payload": {"phase":"validity","agent":"有效性审计Agent"}
  }
]`,
  report: `# GET /api/audits/{id}
# BACKEND_API_KEY 未启用时可删除 -H 参数
curl http://localhost:8086/api/audits/42 -H "X-API-KEY: <backend-key>"

HTTP/1.1 200 OK
{
  "id": 42,
  "tokenId": 12,
  "auditTime": "2026-08-08 14:00:00",
  "status": "running",
  "overallConclusion": null,
  "report": {},
  "progress": 31
}`
}

const filteredSections = computed(() => searchGuideSections(query.value))
const filteredGroups = computed(() => {
  const visible = new Set(filteredSections.value.map((section) => section.id))
  return navigationGroups.map((group) => ({
    ...group,
    items: GUIDE_SECTIONS.filter((section) => group.ids.includes(section.id) && visible.has(section.id))
  }))
})

async function copyCode(key, content) {
  try {
    if (!navigator.clipboard?.writeText) throw new Error("clipboard_unavailable")
    await navigator.clipboard.writeText(content)
    copyState[key] = { role: "status", message: "已复制" }
  } catch {
    copyState[key] = { role: "alert", message: "复制失败，请手动选择代码" }
  }
}
</script>

<style scoped>
.docs-page {
  min-height: 0;
  padding: 0;
  color: var(--ta-text);
  background: transparent;
  border: 0;
  border-radius: 0;
  font-size: 14px;
  font-weight: 400;
}

.docs-search {
  position: sticky;
  top: 66px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 10px 0 14px;
  background: var(--ta-bg);
  border-bottom: 1px solid var(--ta-line);
}

.docs-search label {
  color: var(--ta-muted);
  font-size: 12px;
  white-space: nowrap;
}

.search-control {
  display: flex;
  width: min(560px, 100%);
  height: 38px;
  align-items: center;
  gap: 9px;
  padding: 0 10px;
  background: var(--ta-code);
  border: 1px solid var(--ta-line-strong);
  border-radius: 5px;
}

.search-control:focus-within {
  border-color: var(--ta-green);
}

.search-control > span {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 17px;
}

.search-control input {
  min-width: 0;
  flex: 1;
  color: var(--ta-text);
  background: transparent;
  border: 0;
  outline: 0;
  font: inherit;
}

.search-control input::placeholder {
  color: var(--ta-faint);
}

.docs-layout {
  display: grid;
  grid-template-columns: 166px minmax(0, 1fr) 148px;
  gap: 30px;
  align-items: start;
}

.guide-sidebar,
.toc-sidebar {
  position: sticky;
  top: 135px;
  max-height: calc(100vh - 155px);
  padding-top: 26px;
  overflow-y: auto;
}

.nav-group {
  margin-bottom: 22px;
}

.nav-group p,
.toc-sidebar p {
  margin: 0 0 8px;
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 10px;
  letter-spacing: 0.11em;
  text-transform: uppercase;
}

.nav-group a,
.toc-sidebar a {
  display: block;
  padding: 5px 0;
  color: var(--ta-muted);
  font-size: 12px;
  line-height: 1.45;
  text-decoration: none;
}

.nav-group a:hover,
.toc-sidebar a:hover {
  color: var(--ta-green);
}

.nav-empty {
  color: var(--ta-faint);
  font-size: 12px;
}

.toc-sidebar nav {
  padding-left: 14px;
  border-left: 1px solid var(--ta-line);
}

.guide-article {
  min-width: 0;
  max-width: 760px;
  padding: 48px 0 80px;
}

.article-heading {
  padding-bottom: 32px;
  border-bottom: 1px solid var(--ta-line);
}

.eyebrow {
  margin: 0 0 10px !important;
  color: var(--ta-green) !important;
  font-family: var(--ta-mono);
  font-size: 10px !important;
  letter-spacing: 0.12em;
}

.article-heading h1 {
  margin: 0;
  font-size: clamp(25px, 4vw, 34px);
  font-weight: 680;
  letter-spacing: -0.02em;
}

.article-heading p {
  max-width: 680px;
  margin: 14px 0 0;
  color: var(--ta-muted);
  line-height: 1.8;
}

.guide-article section {
  padding-top: 42px;
  scroll-margin-top: 130px;
}

.guide-article h2,
.guide-article h3 {
  color: var(--ta-text);
  font-weight: 640;
}

.guide-article h2 {
  margin: 0 0 14px;
  font-size: 21px;
}

.guide-article h2 a {
  color: inherit;
  text-decoration: none;
}

.guide-article h2 a:hover::before {
  position: absolute;
  margin-left: -18px;
  color: var(--ta-green);
  content: "#";
}

.guide-article h3 {
  margin: 30px 0 12px;
  font-size: 15px;
  scroll-margin-top: 130px;
}

.guide-article p {
  margin: 0 0 16px;
  color: var(--ta-muted);
  line-height: 1.8;
}

.guide-article strong {
  color: var(--ta-text);
  font-weight: 620;
}

.guide-article :not(pre) > code,
.requirements-list code,
.error-row > code {
  padding: 2px 5px;
  color: #83ebc1;
  background: rgba(67, 224, 162, 0.055);
  border: 1px solid var(--ta-line);
  border-radius: 4px;
  font-family: var(--ta-mono);
  font-size: 0.9em;
}

.requirements-list {
  margin: 22px 0 0;
  border-top: 1px solid var(--ta-line);
}

.requirements-list div {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  gap: 14px;
  padding: 11px 0;
  border-bottom: 1px solid var(--ta-line);
}

.requirements-list dt {
  color: var(--ta-text);
  font-weight: 600;
}

.requirements-list dd {
  margin: 0;
  color: var(--ta-muted);
}

.code-shell,
.endpoint-block {
  margin: 18px 0 20px;
  overflow: hidden;
  background: var(--ta-code);
  border: 1px solid var(--ta-line-strong);
  border-radius: 6px;
}

.code-toolbar,
.endpoint-heading {
  display: flex;
  min-height: 38px;
  align-items: center;
  gap: 9px;
  padding: 0 10px 0 12px;
  color: var(--ta-faint);
  background: var(--ta-panel-raised);
  border-bottom: 1px solid var(--ta-line);
  font-family: var(--ta-mono);
  font-size: 10px;
}

.code-toolbar button,
.endpoint-heading button {
  margin-left: auto;
  padding: 4px 8px;
  color: var(--ta-muted);
  background: transparent;
  border: 1px solid var(--ta-line-strong);
  border-radius: 4px;
  cursor: pointer;
  font: inherit;
}

.code-toolbar button:hover,
.endpoint-heading button:hover {
  color: var(--ta-text);
  border-color: var(--ta-green);
}

.copy-feedback {
  color: var(--ta-green);
  white-space: nowrap;
}

.copy-feedback[role="alert"] {
  color: var(--ta-danger);
}

.code-shell pre,
.endpoint-block pre {
  margin: 0;
  padding: 16px;
  overflow-x: auto;
  color: #c9ded1;
  font-family: var(--ta-mono);
  font-size: 12px;
  line-height: 1.65;
  tab-size: 2;
}

.endpoint-heading > code {
  min-width: 0;
  overflow: hidden;
  color: var(--ta-text);
  font-family: var(--ta-mono);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.method {
  flex: 0 0 auto;
  font-weight: 750;
  letter-spacing: 0.05em;
}

.method--get {
  color: #74c7ec;
}

.method--post {
  color: var(--ta-green);
}

.error-row {
  display: grid;
  grid-template-columns: minmax(120px, 175px) minmax(0, 1fr);
  gap: 16px;
  padding: 14px 0;
  border-top: 1px solid var(--ta-line);
}

.error-row > code {
  align-self: start;
  overflow-wrap: anywhere;
}

.error-row p {
  margin: 0;
}

@media (max-width: 840px) {
  .docs-search {
    top: 111px;
    display: block;
    padding-top: 6px;
  }

  .docs-search label {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .search-control {
    width: 100%;
  }

  .docs-layout {
    display: block;
  }

  .guide-sidebar,
  .toc-sidebar {
    display: none;
  }

  .guide-article {
    max-width: none;
    padding-top: 34px;
  }

  .guide-article section,
  .guide-article h3 {
    scroll-margin-top: 170px;
  }
}

@media (max-width: 520px) {
  .article-heading h1 {
    font-size: 25px;
  }

  .guide-article section {
    padding-top: 34px;
  }

  .requirements-list div,
  .error-row {
    grid-template-columns: 1fr;
    gap: 7px;
  }

  .endpoint-heading {
    gap: 7px;
  }

  .copy-feedback {
    position: absolute;
    left: -9999px;
  }
}
</style>
