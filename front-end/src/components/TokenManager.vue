<template>
  <div class="token-console">
    <section v-reveal class="page-heading" aria-labelledby="token-page-title">
      <div>
        <div class="eyebrow"><span class="signal-dot" />CREDENTIAL REGISTRY / 凭证仓库</div>
        <h1 id="token-page-title">Token 管理</h1>
        <p>录入审计凭证并查看当前可用的 Token 工作区。</p>
      </div>
      <div class="heading-meta" aria-label="Token 数量">
        <span>REGISTERED</span>
        <strong>{{ tokens.length }}</strong>
      </div>
    </section>

    <div class="workspace-grid">
      <section v-reveal class="console-panel form-panel" aria-labelledby="token-form-title">
        <header class="panel-header">
          <div>
            <span class="panel-index">01 / REGISTER</span>
            <h2 id="token-form-title">录入审计 Token</h2>
          </div>
          <span class="panel-note">6 FIELDS</span>
        </header>

        <div class="storage-note" role="note">
          <span class="storage-note__mark">!</span>
          <p><strong>存储说明</strong> Token 当前会保存到后端，用于后续审计调用与历史追溯。请使用专用、可撤销且权限受限的凭证。</p>
        </div>

        <el-form class="token-form" label-position="top" @submit.prevent="save">
          <el-form-item label="名称" required>
            <el-input id="token-name" v-model="form.name" placeholder="例如：生产环境审计" />
            <p class="field-help">用于在审计工作流中辨识此凭证。</p>
          </el-form-item>

          <el-form-item label="Token" required>
            <el-input
              id="token-secret"
              v-model="form.token"
              type="password"
              show-password
              autocomplete="new-password"
              placeholder="输入平台提供的访问 Token"
            />
            <p class="field-help">列表仅显示后端返回的脱敏值；请勿在截图或日志中暴露原文。</p>
          </el-form-item>

          <el-form-item label="平台" required>
            <el-input id="token-platform" v-model="form.platform" placeholder="例如：OpenAI 兼容中转" />
            <p class="field-help">填写 Token 所属服务或中转平台。</p>
          </el-form-item>

          <el-form-item label="Base URL" required>
            <el-input id="token-base-url" v-model="form.tokenBaseUrl" placeholder="https://api.example.com" />
            <p class="field-help">仅填写 http(s) 服务根地址，不附加具体 completions 路径。</p>
          </el-form-item>

          <el-form-item label="宣称模型" required>
            <el-select
              id="claimed-model"
              v-model="form.claimedModel"
              filterable
              allow-create
              default-first-option
              placeholder="选择或输入宣称模型"
            >
              <el-option-group v-for="group in claimedModelGroups" :key="group.label" :label="group.label">
                <el-option v-for="model in group.options" :key="model" :label="model" :value="model" />
              </el-option-group>
            </el-select>
            <p class="field-help">平台声称或接口响应中的目标 model 标识。</p>
          </el-form-item>

          <el-form-item label="非宣称模型" required>
            <el-select
              id="non-claimed-model"
              v-model="form.nonClaimedModel"
              filterable
              allow-create
              default-first-option
              placeholder="选择或输入对照模型"
            >
              <el-option-group v-for="group in nonClaimedModelGroups" :key="group.label" :label="group.label">
                <el-option v-for="model in group.options" :key="model" :label="model" :value="model" />
              </el-option-group>
            </el-select>
            <p class="field-help">用于模型越权与身份边界测试的对照 model。</p>
          </el-form-item>

          <div v-if="formError" data-testid="form-error" class="inline-error" role="alert">
            {{ formError }}
          </div>
          <div v-if="operationError" data-testid="operation-error" class="inline-error" role="alert">
            {{ operationError }}
          </div>

          <div class="form-actions">
            <el-button native-type="submit" type="primary" :loading="saving">保存 Token</el-button>
            <el-button :disabled="saving" @click="reset">重置</el-button>
          </div>
        </el-form>
      </section>

      <section v-reveal class="console-panel list-panel" aria-labelledby="token-list-title">
        <header class="panel-header">
          <div>
            <span class="panel-index">02 / WORKSPACE</span>
            <h2 id="token-list-title">Token 工作区</h2>
          </div>
          <el-button size="small" :loading="loading" @click="reload">刷新</el-button>
        </header>

        <div v-if="loading" data-testid="token-loading" class="state-panel" role="status" aria-live="polite">
          <span class="state-prompt">$</span>
          <div><strong>正在加载 Token</strong><p>正在同步后端凭证索引…</p></div>
        </div>

        <div v-else-if="loadError" data-testid="token-error" class="state-panel state-panel--error" role="alert">
          <span class="state-prompt">!</span>
          <div><strong>Token 列表加载失败</strong><p>{{ loadError }}</p><el-button size="small" @click="reload">重试</el-button></div>
        </div>

        <div v-else-if="tokens.length === 0" data-testid="token-empty" class="state-panel" role="status">
          <span class="state-prompt">_</span>
          <div><strong>暂无 Token</strong><p>完成左侧表单后，凭证会出现在此工作区。</p></div>
        </div>

        <div v-else data-testid="token-table" class="table-scroll" tabindex="0" aria-label="Token 列表，可横向滚动">
          <el-table :data="tokens" class="compact-table" style="width: 100%">
            <el-table-column prop="id" label="ID" width="64" />
            <el-table-column prop="name" label="名称" min-width="130" />
            <el-table-column label="TOKEN" min-width="160">
              <template #default="{ row }"><code class="token-masked">{{ row.tokenMasked }}</code></template>
            </el-table-column>
            <el-table-column prop="platform" label="平台" min-width="120" />
            <el-table-column prop="claimedModel" label="宣称模型" min-width="150" />
            <el-table-column label="操作" width="88">
              <template #default="{ row }">
                <el-button class="delete-button" type="danger" plain size="small" @click="remove(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { createToken, deleteToken, listTokens } from "../request/api"
import { isUrl, required } from "../utils/validate"

const tokens = ref([])
const loading = ref(true)
const saving = ref(false)
const loadError = ref("")
const formError = ref("")
const operationError = ref("")

const claimedModelGroups = [
  { label: "OpenAI", options: ["gpt-5.4", "gpt-5.3", "gpt-5.2", "o1", "o1-mini", "gpt-4o", "gpt-4o-mini"] },
  { label: "Anthropic", options: ["claude-opus-4.6", "claude-opus-4-6", "claude-sonnet-4", "claude-3-5-sonnet", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku"] },
  { label: "Google", options: ["gemini-1.5-pro", "gemini-1.5-flash"] },
  { label: "Mistral", options: ["mistral-large-latest", "mistral-small-latest", "codestral-latest"] },
  { label: "Meta", options: ["llama-3.1-405b-instruct", "llama-3.1-70b-instruct", "llama-3.1-8b-instruct"] },
  { label: "Cohere", options: ["command-r-plus", "command-r"] },
  { label: "xAI", options: ["grok-2"] }
]

const nonClaimedModelGroups = [
  { label: "轻量快速", options: ["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash", "mistral-small-latest"] },
  { label: "强力对照", options: ["o1", "gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro", "mistral-large-latest"] }
]

const form = reactive({
  name: "",
  token: "",
  platform: "",
  tokenBaseUrl: "",
  claimedModel: "",
  nonClaimedModel: ""
})

function errorText(error, fallback) {
  return error?.response?.data?.error || error?.message || fallback
}

function reset() {
  form.name = ""
  form.token = ""
  form.platform = ""
  form.tokenBaseUrl = ""
  form.claimedModel = ""
  form.nonClaimedModel = ""
  formError.value = ""
  operationError.value = ""
}

async function reload() {
  loading.value = true
  loadError.value = ""
  try {
    tokens.value = (await listTokens()) || []
  } catch (error) {
    loadError.value = errorText(error, "加载失败")
    ElMessage.error(loadError.value)
  } finally {
    loading.value = false
  }
}

async function save() {
  formError.value = ""
  operationError.value = ""
  const fields = [form.name, form.token, form.platform, form.tokenBaseUrl, form.claimedModel, form.nonClaimedModel]
  if (fields.some((value) => !required(value))) {
    formError.value = "请补全必填项后再保存。"
    return
  }
  if (!isUrl(form.tokenBaseUrl)) {
    formError.value = "Base URL 格式不正确，请输入 http(s) 地址。"
    return
  }
  saving.value = true
  try {
    await createToken({ ...form })
    ElMessage.success("Token 已保存")
    reset()
    await reload()
  } catch (error) {
    operationError.value = errorText(error, "保存失败")
    ElMessage.error(operationError.value)
  } finally {
    saving.value = false
  }
}

async function remove(id) {
  try {
    await ElMessageBox.confirm("确认删除该 Token？删除后将无法用于新的审计。", "删除 Token", { type: "warning" })
  } catch {
    return
  }
  operationError.value = ""
  try {
    await deleteToken(id)
    ElMessage.success("Token 已删除")
    await reload()
  } catch (error) {
    operationError.value = errorText(error, "删除失败")
    ElMessage.error(operationError.value)
  }
}

onMounted(reload)
</script>

<style scoped>
.token-console { display: grid; gap: 14px; width: 100%; max-width: 1480px; margin: 0 auto; }
.page-heading { display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 5px 0 10px; border-bottom: 1px solid var(--ta-line); }
.eyebrow, .panel-index, .panel-note, .heading-meta, .field-help, .state-panel, .token-masked { font-family: var(--ta-mono); }
.eyebrow { display: flex; align-items: center; gap: 8px; color: var(--ta-green); font-size: 10px; letter-spacing: .08em; }
.signal-dot { width: 6px; height: 6px; background: var(--ta-green); border-radius: 50%; }
.page-heading h1 { margin: 4px 0 1px; color: var(--ta-text); font-size: clamp(23px, 2.8vw, 32px); font-weight: 650; letter-spacing: -.035em; }
.page-heading p { margin: 0; color: var(--ta-muted); font-size: 12px; }
.heading-meta { display: grid; gap: 1px; justify-items: end; color: var(--ta-faint); font-size: 9px; letter-spacing: .08em; }
.heading-meta strong { color: var(--ta-green); font-size: 20px; font-weight: 600; }
.workspace-grid { display: grid; grid-template-columns: minmax(340px, .78fr) minmax(520px, 1.22fr); gap: 14px; align-items: start; }
.console-panel { min-width: 0; overflow: hidden; background: var(--ta-panel); border: 1px solid var(--ta-line); border-radius: var(--ta-radius); }
.panel-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 57px; padding: 10px 14px; background: var(--ta-panel-raised); border-bottom: 1px solid var(--ta-line); }
.panel-index { display: block; margin-bottom: 2px; color: var(--ta-green); font-size: 9px; letter-spacing: .1em; }
.panel-header h2 { margin: 0; color: var(--ta-text); font-size: 15px; font-weight: 650; }
.panel-note { color: var(--ta-faint); font-size: 9px; letter-spacing: .08em; }
.storage-note { display: flex; gap: 9px; margin: 13px 14px 0; padding: 9px 10px; color: var(--ta-muted); background: var(--ta-code); border: 1px solid rgba(233, 187, 99, .18); border-radius: 4px; }
.storage-note__mark { color: var(--ta-amber); font-family: var(--ta-mono); }
.storage-note p { margin: 0; font-size: 11px; line-height: 1.55; }
.storage-note strong { color: var(--ta-text); font-weight: 600; }
.token-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 12px; padding: 13px 14px 14px; }
.token-form :deep(.el-form-item) { min-width: 0; margin-bottom: 13px; }
.token-form :deep(.el-form-item__label) { height: auto; margin-bottom: 5px; color: var(--ta-text) !important; font-family: var(--ta-mono); font-size: 10px; line-height: 1.4; letter-spacing: .04em; }
.token-form :deep(.el-select) { width: 100%; }
.field-help { width: 100%; margin: 5px 0 0; color: var(--ta-faint); font-size: 9px; line-height: 1.45; }
.inline-error { grid-column: 1 / -1; margin-bottom: 10px; padding: 8px 10px; color: var(--ta-danger); background: rgba(255, 125, 121, .055); border: 1px solid rgba(255, 125, 121, .2); border-radius: 4px; font-size: 11px; }
.form-actions { display: flex; grid-column: 1 / -1; gap: 8px; padding-top: 1px; }
.form-actions :deep(.el-button) { margin-left: 0; }
.state-panel { display: flex; gap: 12px; min-height: 190px; padding: 24px; color: var(--ta-muted); }
.state-prompt { color: var(--ta-green); }
.state-panel--error .state-prompt, .state-panel--error strong { color: var(--ta-danger); }
.state-panel strong { color: var(--ta-text); font-size: 12px; font-weight: 550; }
.state-panel p { margin: 5px 0 11px; color: var(--ta-faint); font-size: 10px; }
.table-scroll { overflow-x: auto; }
.compact-table { min-width: 720px; }
.compact-table :deep(.el-table__cell) { padding: 8px 0; }
.compact-table :deep(.cell) { font-size: 11px; }
.token-masked { color: var(--ta-green); font-size: 10px; white-space: nowrap; }
.delete-button { color: var(--ta-danger) !important; background: rgba(255, 125, 121, .045) !important; border-color: rgba(255, 125, 121, .22) !important; }
.delete-button:hover, .delete-button:focus-visible { background: rgba(255, 125, 121, .1) !important; border-color: rgba(255, 125, 121, .42) !important; }
@media (max-width: 900px) { .workspace-grid { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .page-heading { align-items: flex-start; } .token-form { grid-template-columns: 1fr; } .form-actions :deep(.el-button) { flex: 1; } }
</style>
