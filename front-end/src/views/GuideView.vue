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
          <p class="eyebrow">TOKENAUDIT / DOCUMENTATION</p>
          <h1>接入与审计指南</h1>
          <p>
            面向 OpenAI 兼容中转站的完整使用说明。先配置审计 AI，再录入目标 Token；系统会在正式审计前验证链路，
            并支持多个任务并行执行、独立终止与证据回溯。后端默认运行在 <code>http://localhost:8086</code>。
          </p>
        </div>

        <section id="overview" v-reveal>
          <h2><a href="#overview">工作流概览</a></h2>
          <div class="workflow-grid">
            <article><span>01</span><strong>配置审计 AI</strong><p>在设置中保存判定模型、完整推理 URL、API Key 与有效期。</p></article>
            <article><span>02</span><strong>录入中转 Token</strong><p>填写中转站地址和真实模型 ID，平台名称仅用于识别。</p></article>
            <article><span>03</span><strong>预检后审计</strong><p>链路通过后进入六维审计；多个任务可同时执行或排队。</p></article>
            <article><span>04</span><strong>查看证据</strong><p>实时事件、终态与报告彼此关联，失败时可直接定位原因。</p></article>
          </div>
          <div class="docs-callout docs-callout--info">
            <strong>两类模型不要混淆</strong>
            <p><b>目标模型</b>是被审计的中转站模型；<b>审计 AI</b>负责阅读证据并给出判定，二者应分别配置。</p>
          </div>
        </section>

        <section id="requirements" v-reveal>
          <h2><a href="#requirements">运行要求</a></h2>
          <p>
            准备 Node.js 与 npm、Java 与 Maven，以及 Python 3。前端与 API 是常驻服务；审计核心由 API 在收到任务后拉起。
          </p>
          <dl class="requirements-list">
            <div><dt>前端</dt><dd>Vue 3 + Vite，开发端口 <code>5173</code></dd></div>
            <div><dt>后端</dt><dd>Spring Boot，API 端口 <code>8086</code></dd></div>
            <div><dt>审计核心</dt><dd>Python 模块 <code>audit_core</code></dd></div>
            <div><dt>配置存储</dt><dd>Redis 数据库 <code>1</code>（界面中显示为 B01）</dd></div>
          </dl>
        </section>

        <section id="configure" v-reveal>
          <h2><a href="#configure">系统与 Redis</a></h2>
          <p>
            在仓库根目录创建 <code>.env</code>。这里只保存运行参数，不再把审计模型密钥固定为 DeepSeek；
            审计 AI 的服务商、模型与密钥统一在前端“设置”中管理。
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

        <section id="audit-ai" v-reveal>
          <h2><a href="#audit-ai">配置审计 AI</a></h2>
          <p>
            点击右上角“设置”，在“审计判定模型”中配置一个可用的 OpenAI 兼容模型。服务商只是界面预设，
            可选择 OpenAI、Anthropic、DeepSeek、xAI、Moonshot、阿里云、智谱等，也可以直接输入自定义服务商和模型。
          </p>
          <dl class="field-list">
            <div><dt>API URL</dt><dd>填写完整推理端点，例如 <code>https://api.example.com/v1/chat/completions</code></dd></div>
            <div><dt>模型</dt><dd>填写该 API Key 实际有权调用的模型 ID，不能只写产品展示名称</dd></div>
            <div><dt>API Key</dt><dd>保存后加密写入 Redis；读取配置时不会回传明文</dd></div>
            <div><dt>有效期</dt><dd><code>1–43200</code> 分钟；每次重新保存都会从当前时刻重置过期时间</dd></div>
          </dl>
          <div class="docs-callout docs-callout--warning">
            <strong>开始审计前必须配置</strong>
            <p>如果配置不存在或已过期，点击“开始审计”会自动打开设置面板，并提示配置审计 API Key。</p>
          </div>
          <div class="endpoint-block" data-testid="copy-audit-ai">
            <div class="endpoint-heading">
              <span class="method method--put">PUT</span>{{ " " }}<code>/api/settings/audit-ai</code>
              <button type="button" aria-label="复制审计 AI 配置示例" @click="copyCode('auditAi', codeSamples.auditAi)">复制</button>
              <span v-if="copyState.auditAi" class="copy-feedback" :role="copyState.auditAi.role" aria-live="polite">{{ copyState.auditAi.message }}</span>
            </div>
            <pre><code>{{ codeSamples.auditAi }}</code></pre>
          </div>
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
            可在“Token 管理”页面录入，也可调用 <code>POST /api/tokens</code>。API 地址既可填写基础地址（允许 <code>/api/v1</code> 等路径），
            也可填写完整的 <code>/chat/completions</code> 或 <code>/responses</code> 推理端点。平台名称仅作备注，模型 ID 会原样发送。
            接口返回掩码后的 <code>tokenMasked</code>，不会回传明文。
          </p>
          <div class="example-grid">
            <article><strong>OpenRouter</strong><code>https://openrouter.ai/api/v1</code><span>模型示例：openai/gpt-4o-mini</span></article>
            <article><strong>AiHubMix</strong><code>https://aihubmix.com/v1</code><span>模型必须以控制台实际支持的 ID 为准</span></article>
            <article><strong>其他中转站</strong><code>https://relay.example.com/v1</code><span>兼容 OpenAI Chat Completions 或 Responses</span></article>
          </div>
          <div class="docs-callout docs-callout--info">
            <strong>中转站只配置在 Token 工作区</strong>
            <p>“审计 AI 设置”不提供中转站选项，避免让同一个待审计中转站充当自己的审计者。</p>
          </div>
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

        <section id="models" v-reveal>
          <h2><a href="#models">选择与修改模型</a></h2>
          <p>
            审计 AI 模型和 Token 的声明模型都使用“可输入下拉框”：常见模型可以直接选择，不在目录中的模型也可以手动输入。
            目录只是输入辅助，不代表某个中转站一定支持这些模型；最终应以服务商模型列表或一次真实调用为准。
          </p>
          <div class="status-grid">
            <article><span>常见格式</span><strong><code>gpt-4o-mini</code></strong><p>官方或直连服务常见写法</p></article>
            <article><span>聚合格式</span><strong><code>openai/gpt-4o-mini</code></strong><p>OpenRouter 等聚合平台常见写法</p></article>
            <article><span>完整模型 ID</span><strong><code>Qwen/Qwen3-8B</code></strong><p>硅基流动等平台常见写法</p></article>
          </div>
          <p>
            已录入的 Token 可以在工作区直接修改声明模型。修改只影响后续审计，不会篡改历史报告中的模型信息。
          </p>
          <div class="endpoint-block" data-testid="copy-update-model">
            <div class="endpoint-heading">
              <span class="method method--put">PUT</span>{{ " " }}<code>/api/tokens/{id}/model</code>
              <button type="button" aria-label="复制修改声明模型示例" @click="copyCode('updateModel', codeSamples.updateModel)">复制</button>
              <span v-if="copyState.updateModel" class="copy-feedback" :role="copyState.updateModel.role" aria-live="polite">{{ copyState.updateModel.message }}</span>
            </div>
            <pre><code>{{ codeSamples.updateModel }}</code></pre>
          </div>
        </section>

        <section id="run-audit" v-reveal>
          <h2><a href="#run-audit">预检与发起审计</a></h2>
          <p>
            每次任务都会先执行中转站前置预检，以最小请求验证 Base URL、Token 鉴权、声明模型和 OpenAI 兼容响应格式。
            预检失败时会写入 <code>preflight_end</code>、<code>audit_aborted</code> 和 <code>audit_failed</code> 事件并立即停止，不会启动任何审计 Agent。
          </p>
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

        </section>

        <section id="parallel" v-reveal>
          <h2><a href="#parallel">并行与终止任务</a></h2>
          <p>
            一个任务运行时，“开始审计”会变为“并行新建审计”，不会锁住表单。默认最多同时执行
            <code>4</code> 个任务，额外任务进入容量为 <code>20</code> 的队列；这两个值可通过
            <code>AUDIT_MAX_CONCURRENCY</code> 与 <code>AUDIT_QUEUE_CAPACITY</code> 调整。
          </p>
          <div class="status-grid">
            <article><span>executionState</span><strong>queued</strong><p>任务已创建，正在等待执行槽位</p></article>
            <article><span>executionState</span><strong>active</strong><p>Python 审计进程正在运行</p></article>
            <article><span>status</span><strong>cancelled</strong><p>用户已终止，不再生成完整报告</p></article>
          </div>
          <p>
            任务卡片可以切换查看不同审计的实时管线，也可以单独终止。终止运行任务时，后端会中断 Future、销毁 Python 进程及其子进程；
            对已经完成、失败或终止的任务重复调用取消接口不会改写历史结果。
          </p>
          <div class="endpoint-block" data-testid="copy-cancel">
            <div class="endpoint-heading">
              <span class="method method--delete">POST</span>{{ " " }}<code>/api/audits/{id}/cancel</code>
              <button type="button" aria-label="复制终止审计示例" @click="copyCode('cancel', codeSamples.cancel)">复制</button>
              <span v-if="copyState.cancel" class="copy-feedback" :role="copyState.cancel.role" aria-live="polite">{{ copyState.cancel.message }}</span>
            </div>
            <pre><code>{{ codeSamples.cancel }}</code></pre>
          </div>
        </section>

        <section id="events" v-reveal>
          <h2><a href="#events">读取实时事件</a></h2>
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
            查询接口返回 <code>status</code>、<code>executionState</code>、<code>progress</code> 与 <code>report</code>。
            只有状态为 <code>completed</code> 时才会生成完整报告；<code>failed</code> 和 <code>cancelled</code> 应结合事件列表排查或确认原因。
            导出文件写入配置的报告目录，历史页面不会因为之后修改声明模型而改变旧报告。
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

        <section id="security" v-reveal>
          <h2><a href="#security">密钥与安全边界</a></h2>
          <div class="security-list">
            <article><strong>目标 Token</strong><p>后端加密保存，列表接口只返回掩码；加密密钥默认写入本地 <code>data/token-encryption.key</code>。</p></article>
            <article><strong>审计 AI Key</strong><p>加密写入 Redis B01，并受用户设置的 TTL 控制；配置查询接口不会回传明文。</p></article>
            <article><strong>后端访问密钥</strong><p><code>BACKEND_API_KEY</code> 用于保护本项目 API，与中转 Token、审计 AI Key 都不是一回事。</p></article>
            <article><strong>目标地址限制</strong><p>默认拒绝私网审计目标；仅在可信开发环境中考虑启用 <code>AUDIT_ALLOW_PRIVATE_TARGETS</code>。</p></article>
          </div>
          <div class="docs-callout docs-callout--warning">
            <strong>不要提交秘密</strong>
            <p>不要把 <code>.env</code>、API Key、Token、Redis 密码或运行日志提交到 Git 仓库；仓库只保留无密钥的 <code>.env.example</code>。</p>
          </div>
        </section>

        <section id="errors" v-reveal>
          <h2><a href="#errors">常见错误</a></h2>
          <div class="error-row">
            <code>401 / 403</code>
            <p>确认后端是否设置了 <code>BACKEND_API_KEY</code>，并让 <code>X-API-KEY</code> 与其一致。</p>
          </div>
          <div class="error-row">
            <code>audit_ai_not_configured</code>
            <p>审计 AI 配置不存在或已过期；打开设置重新填写 API Key 并保存，TTL 会从本次保存重新计算。</p>
          </div>
          <div class="error-row">
            <code>preflight_end: failed</code>
            <p>目标中转站没有打通。优先核对完整 URL、鉴权 Token 和模型 ID；系统会停止审计，避免继续产生无效调用。</p>
          </div>
          <div class="error-row">
            <code>audit_queue_full</code>
            <p>当前运行与排队任务已达到上限。等待已有任务结束、终止不需要的任务，或调整并发与队列配置。</p>
          </div>
          <div class="error-row">
            <code>Model Not Exist</code>
            <p>先判断错误来自目标中转模型还是审计 AI，再检查对应位置的模型 ID 是否属于当前 API Key。</p>
          </div>
          <div class="error-row">
            <code>Cannot run program "python"</code>
            <p>确认 Python 位于 PATH，或通过 <code>PYTHON_EXECUTABLE</code> 指定可执行文件。</p>
          </div>
          <div class="error-row">
            <code>Network Error / 503</code>
            <p>确认后端 8086 可访问、前端 <code>VITE_BACKEND_BASE_URL</code> 正确，并读取失败事件中的 endpoint、message 与 status。</p>
          </div>
          <div class="error-row">
            <code>python_audit_timeout</code>
            <p>单个审计超过 <code>AUDIT_PROCESS_TIMEOUT_SECONDS</code>；检查目标服务延迟，必要时提高超时或降低并行压力。</p>
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
  { label: "开始", ids: ["overview", "requirements", "configure", "audit-ai", "start"] },
  { label: "目标配置", ids: ["token", "models"] },
  { label: "审计工作流", ids: ["run-audit", "parallel", "events", "report"] },
  { label: "参考", ids: ["security", "errors"] }
]

const tableOfContents = [
  { id: "overview", title: "工作流概览" },
  { id: "requirements", title: "运行要求" },
  { id: "configure", title: "系统与 Redis" },
  { id: "audit-ai", title: "配置审计 AI" },
  { id: "start", title: "启动项目" },
  { id: "token", title: "录入 Token" },
  { id: "models", title: "选择与修改模型" },
  { id: "run-audit", title: "预检与发起审计" },
  { id: "parallel", title: "并行与终止任务" },
  { id: "events", title: "读取实时事件" },
  { id: "report", title: "查看报告" },
  { id: "security", title: "密钥与安全边界" },
  { id: "errors", title: "常见错误" }
]

const codeSamples = {
  environment: `BACKEND_API_KEY=
APP_ENVIRONMENT=development
BACKEND_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DATABASE=1

TOKEN_ENCRYPTION_KEY=
TOKEN_ENCRYPTION_KEY_FILE=../data/token-encryption.key
AUDIT_ALLOW_PRIVATE_TARGETS=false
AUDIT_MAX_CONCURRENCY=4
AUDIT_QUEUE_CAPACITY=20
AUDIT_PROCESS_TIMEOUT_SECONDS=900
PYTHON_EXECUTABLE=python
AUDIT_CORE_WORKDIR=../audit-core
AUDIT_EXPORT_FORMATS=json,md,xlsx`,
  frontEnvironment: `VITE_BACKEND_BASE_URL=http://localhost:8086`,
  auditAi: `# PUT /api/settings/audit-ai
curl --request PUT http://localhost:8086/api/settings/audit-ai \
  --header "Content-Type: application/json" \
  --header "X-API-KEY: <backend-key>" \
  --data '{"provider":"OpenAI compatible","apiUrl":"https://api.example.com/v1/chat/completions","model":"deepseek-chat","apiKey":"<audit-ai-key>","ttlMinutes":1440}'

# GET 只返回掩码与配置状态，不返回 API Key 明文
curl http://localhost:8086/api/settings/audit-ai -H "X-API-KEY: <backend-key>"`,
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
  --data '{"name":"production-relay","token":"sk-...","platform":"relay","tokenBaseUrl":"https://api.example.com/v1","claimedModel":"claude-opus-4-6","nonClaimedModel":"gpt-4o-mini"}'`,
  updateModel: `# PUT /api/tokens/{id}/model
curl --request PUT http://localhost:8086/api/tokens/12/model \
  --header "Content-Type: application/json" \
  --header "X-API-KEY: <backend-key>" \
  --data '{"claimedModel":"openai/gpt-4o-mini"}'`,
  audit: `# POST /api/audits；BACKEND_API_KEY 未启用时可删除 X-API-KEY 请求头
curl --request POST http://localhost:8086/api/audits \\
  --header "Content-Type: application/json" \\
  --header "X-API-KEY: <backend-key>" \\
  --data '{"tokenId":12,"exportFormats":["json","md"],"auditDimensions":["validity","permission","watering","compliance","stability","security"]}'

HTTP/1.1 200 OK
{"auditId":42,"report":null}`,
  cancel: `# POST /api/audits/{id}/cancel
curl --request POST http://localhost:8086/api/audits/42/cancel \
  --header "X-API-KEY: <backend-key>"

HTTP/1.1 200 OK
{"id":42,"status":"cancelled","progress":100,"executionState":"cancelled"}`,
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
  "executionState": "active",
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

.workflow-grid,
.example-grid,
.status-grid,
.security-list {
  display: grid;
  gap: 10px;
  margin: 20px 0;
}

.workflow-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.example-grid,
.status-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.security-list { grid-template-columns: repeat(2, minmax(0, 1fr)); }

.workflow-grid article,
.example-grid article,
.status-grid article,
.security-list article {
  min-width: 0;
  padding: 14px;
  background: rgba(10, 24, 17, 0.54);
  border: 1px solid var(--ta-line);
  border-radius: 6px;
}

.workflow-grid article > span,
.status-grid article > span {
  display: block;
  margin-bottom: 8px;
  color: var(--ta-green);
  font-family: var(--ta-mono);
  font-size: 9px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.workflow-grid strong,
.example-grid strong,
.status-grid strong,
.security-list strong {
  display: block;
  margin-bottom: 6px;
}

.workflow-grid p,
.example-grid span,
.status-grid p,
.security-list p {
  display: block;
  margin: 0;
  color: var(--ta-muted);
  font-size: 12px;
  line-height: 1.65;
}

.example-grid code {
  display: block;
  margin: 7px 0;
  overflow-wrap: anywhere;
}

.docs-callout {
  margin: 20px 0;
  padding: 13px 15px;
  background: rgba(116, 199, 236, 0.045);
  border: 1px solid rgba(116, 199, 236, 0.2);
  border-left: 3px solid #74c7ec;
  border-radius: 5px;
}

.docs-callout--warning {
  background: rgba(233, 187, 99, 0.045);
  border-color: rgba(233, 187, 99, 0.2);
  border-left-color: #e9bb63;
}

.docs-callout strong { display: block; margin-bottom: 4px; }
.docs-callout p { margin: 0; font-size: 12px; }
.docs-callout b { color: var(--ta-text); font-weight: 620; }

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

.field-list {
  margin: 20px 0;
  border: 1px solid var(--ta-line);
  border-radius: 6px;
}

.field-list div {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 16px;
  padding: 11px 13px;
  border-bottom: 1px solid var(--ta-line);
}

.field-list div:last-child { border-bottom: 0; }
.field-list dt { color: var(--ta-text); font-weight: 620; }
.field-list dd { margin: 0; color: var(--ta-muted); line-height: 1.65; }

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

.method--put { color: #e9bb63; }
.method--delete { color: var(--ta-danger); }

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
  .field-list div,
  .error-row {
    grid-template-columns: 1fr;
    gap: 7px;
  }

  .workflow-grid,
  .example-grid,
  .status-grid,
  .security-list {
    grid-template-columns: 1fr;
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
