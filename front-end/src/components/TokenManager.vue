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
          <span class="panel-note">5 CORE + 1 OPTIONAL</span>
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

          <el-form-item label="平台（仅备注）" required>
            <el-input id="token-platform" v-model="form.platform" placeholder="例如：自建中转 / 第三方服务" />
            <p class="field-help">仅用于列表识别，不参与端点拼接、鉴权或模型判断。</p>
          </el-form-item>

          <el-form-item label="API 地址" required>
            <el-input id="token-base-url" v-model="form.tokenBaseUrl" placeholder="https://api.example.com/v1" />
            <p class="field-help">可填写基础地址或完整的 /chat/completions、/responses 端点；基础地址默认按 OpenAI Chat Completions 协议补全。</p>
          </el-form-item>

          <el-form-item label="宣称模型" required>
            <ModelCombobox
              id="claimed-model"
              v-model="form.claimedModel"
              :groups="claimedModelGroups"
              placeholder="输入完整模型 ID，或选择常见格式"
            />
            <p class="field-help">可直接输入并保留任意 model 标识；建议复制服务商 /v1/models 返回的完整 ID，系统不会改写。</p>
          </el-form-item>

          <el-form-item class="target-audit-option" label="目标模型审计">
            <div class="target-audit-control">
              <div>
                <strong>{{ form.enableTargetModelAudit ? "已启用" : "已关闭" }}</strong>
                <p>开启后会额外调用一个目标模型，用于验证 Token 的模型权限边界。</p>
              </div>
              <el-switch
                id="target-model-audit"
                v-model="form.enableTargetModelAudit"
                inline-prompt
                active-text="开"
                inactive-text="关"
                aria-label="是否启用目标模型审计"
                @change="handleTargetAuditChange"
              />
            </div>
            <p class="field-help">支持多模型的中转站通常保持关闭；仅在需要验证模型权限边界时开启。</p>
          </el-form-item>

          <el-form-item v-if="form.enableTargetModelAudit" class="target-model-field" label="目标审计模型" required>
            <ModelCombobox
              id="non-claimed-model"
              v-model="form.nonClaimedModel"
              :groups="nonClaimedModelGroups"
              placeholder="输入完整目标模型 ID，或选择常见格式"
            />
            <p class="field-help">仅在启用后调用；应填写预期不在当前 Token 权限内的 model。</p>
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
            <el-table-column label="API 地址" min-width="320">
              <template #default="{ row }">
                <div class="url-cell" :data-testid="`url-editor-${row.id}`">
                  <el-input
                    :id="`token-base-url-${row.id}`"
                    v-model="urlDrafts[row.id]"
                    :disabled="updatingUrlIds.has(row.id)"
                    placeholder="https://api.example.com/v1"
                    @keyup.enter="saveTokenBaseUrl(row)"
                  >
                    <template #append>
                      <el-button
                        :loading="updatingUrlIds.has(row.id)"
                        :aria-label="`保存 ${row.name} 的 API 地址`"
                        @click="saveTokenBaseUrl(row)"
                      >保存</el-button>
                    </template>
                  </el-input>
                  <span class="url-hint">支持基础地址或完整推理端点</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="宣称模型" min-width="280">
              <template #default="{ row }">
                <div class="model-cell" :data-testid="`model-selector-${row.id}`">
                  <ModelCombobox
                    :id="`claimed-model-selector-${row.id}`"
                    v-model="modelDrafts[row.id]"
                    :groups="claimedModelGroups"
                    placeholder="输入或选择模型 ID"
                    :disabled="updatingModelIds.has(row.id)"
                    @commit="saveClaimedModel(row, $event)"
                  />
                  <span v-if="updatingModelIds.has(row.id)" class="model-save-state">保存中...</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="目标模型审计" min-width="150">
              <template #default="{ row }">
                <span v-if="row.nonClaimedModel" class="target-state target-state--on">已启用 · {{ row.nonClaimedModel }}</span>
                <span v-else class="target-state">已关闭</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="88">
              <template #default="{ row }">
                <el-button
                  class="delete-button"
                  type="danger"
                  plain
                  size="small"
                  :loading="deletingIds.has(row.id)"
                  @click="remove(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import ModelCombobox from "./ModelCombobox.vue"
import { MODEL_GROUPS } from "../constants/modelCatalog"
import {
  createToken,
  deleteToken,
  listTokens,
  updateTokenBaseUrl,
  updateTokenClaimedModel
} from "../request/api"
import { isBaseUrl, required } from "../utils/validate"

const tokens = ref([])
const loading = ref(true)
const saving = ref(false)
const loadError = ref("")
const formError = ref("")
const operationError = ref("")
const deletingIds = ref(new Set())
const modelDrafts = reactive({})
const urlDrafts = reactive({})
const updatingModelIds = ref(new Set())
const updatingUrlIds = ref(new Set())
let requestSequence = 0
let componentAlive = true

const claimedModelGroups = MODEL_GROUPS
const nonClaimedModelGroups = MODEL_GROUPS

const form = reactive({
  name: "",
  token: "",
  platform: "",
  tokenBaseUrl: "",
  claimedModel: "",
  enableTargetModelAudit: false,
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
  form.enableTargetModelAudit = false
  form.nonClaimedModel = ""
  formError.value = ""
  operationError.value = ""
}

async function reload() {
  const sequence = ++requestSequence
  loading.value = true
  loadError.value = ""
  tokens.value = []
  try {
    const loadedTokens = await listTokens()
    if (!componentAlive || sequence !== requestSequence) return
    tokens.value = loadedTokens || []
    syncDrafts(tokens.value)
  } catch (error) {
    if (!componentAlive || sequence !== requestSequence) return
    loadError.value = errorText(error, "加载失败")
    ElMessage.error(loadError.value)
  } finally {
    if (componentAlive && sequence === requestSequence) loading.value = false
  }
}

async function save() {
  if (saving.value) return
  formError.value = ""
  operationError.value = ""
  const fields = [form.name, form.token, form.platform, form.tokenBaseUrl, form.claimedModel]
  if (fields.some((value) => !required(value))) {
    formError.value = "请补全必填项后再保存。"
    return
  }
  if (form.enableTargetModelAudit && !required(form.nonClaimedModel)) {
    formError.value = "启用目标模型审计后，请填写目标审计模型。"
    return
  }
  if (!isBaseUrl(form.tokenBaseUrl)) {
    formError.value = "API 地址必须是安全的 http(s) 地址，可填写基础地址或完整推理端点，但不能包含查询参数、片段或用户信息。"
    return
  }
  saving.value = true
  try {
    await createToken({
      name: form.name,
      token: form.token,
      platform: form.platform,
      tokenBaseUrl: form.tokenBaseUrl,
      claimedModel: form.claimedModel,
      nonClaimedModel: form.enableTargetModelAudit ? form.nonClaimedModel : ""
    })
    if (!componentAlive) return
    ElMessage.success("Token 已保存")
    reset()
    await reload()
  } catch (error) {
    if (!componentAlive) return
    operationError.value = errorText(error, "保存失败")
    ElMessage.error(operationError.value)
  } finally {
    if (componentAlive) saving.value = false
  }
}

function handleTargetAuditChange(enabled) {
  if (!enabled) form.nonClaimedModel = ""
  formError.value = ""
}

function syncDrafts(items) {
  const activeIds = new Set(items.map((token) => String(token.id)))
  for (const id of Object.keys(modelDrafts)) {
    if (!activeIds.has(id)) delete modelDrafts[id]
  }
  for (const id of Object.keys(urlDrafts)) {
    if (!activeIds.has(id)) delete urlDrafts[id]
  }
  for (const token of items) {
    if (!updatingModelIds.value.has(token.id)) modelDrafts[token.id] = token.claimedModel || ""
    if (!updatingUrlIds.value.has(token.id)) urlDrafts[token.id] = token.tokenBaseUrl || ""
  }
}

async function saveTokenBaseUrl(row) {
  if (updatingUrlIds.value.has(row.id)) return
  const tokenBaseUrl = String(urlDrafts[row.id] || "").trim()
  if (!isBaseUrl(tokenBaseUrl)) {
    operationError.value = "API 地址必须是安全的 http(s) 地址，不能包含查询参数、片段或用户信息。"
    urlDrafts[row.id] = row.tokenBaseUrl || ""
    return
  }
  if (tokenBaseUrl === row.tokenBaseUrl) return

  updatingUrlIds.value.add(row.id)
  operationError.value = ""
  try {
    const updated = await updateTokenBaseUrl(row.id, tokenBaseUrl)
    if (!componentAlive) return
    const index = tokens.value.findIndex((token) => token.id === row.id)
    if (index >= 0) tokens.value[index] = updated
    urlDrafts[row.id] = updated.tokenBaseUrl
    modelDrafts[row.id] = updated.claimedModel || ""
    ElMessage.success("API 地址已更新")
  } catch (error) {
    if (!componentAlive) return
    urlDrafts[row.id] = row.tokenBaseUrl || ""
    operationError.value = errorText(error, "API 地址更新失败")
    ElMessage.error(operationError.value)
  } finally {
    if (componentAlive) updatingUrlIds.value.delete(row.id)
  }
}

async function saveClaimedModel(row, selectedModel) {
  if (updatingModelIds.value.has(row.id)) return
  const claimedModel = String(selectedModel || "").trim()
  if (!required(claimedModel)) {
    operationError.value = "请先选择或输入宣称模型。"
    modelDrafts[row.id] = row.claimedModel || ""
    return
  }
  if (claimedModel === row.claimedModel) return

  updatingModelIds.value.add(row.id)
  operationError.value = ""
  try {
    const updated = await updateTokenClaimedModel(row.id, claimedModel)
    if (!componentAlive) return
    const index = tokens.value.findIndex((token) => token.id === row.id)
    if (index >= 0) tokens.value[index] = updated
    modelDrafts[row.id] = updated.claimedModel
    ElMessage.success("宣称模型已更新")
  } catch (error) {
    if (!componentAlive) return
    modelDrafts[row.id] = row.claimedModel || ""
    operationError.value = errorText(error, "模型更新失败")
    ElMessage.error(operationError.value)
  } finally {
    if (componentAlive) updatingModelIds.value.delete(row.id)
  }
}

async function remove(id) {
  try {
    await ElMessageBox.confirm("确认删除该 Token？删除后将无法用于新的审计。", "删除 Token", { type: "warning" })
  } catch (error) {
    if (error === "cancel" || error === "close") return
    if (!componentAlive) return
    operationError.value = errorText(error, "删除确认失败")
    ElMessage.error(operationError.value)
    return
  }
  if (!componentAlive || deletingIds.value.has(id)) return
  operationError.value = ""
  deletingIds.value.add(id)
  try {
    await deleteToken(id)
    if (!componentAlive) return
    ElMessage.success("Token 已删除")
    await reload()
  } catch (error) {
    if (!componentAlive) return
    operationError.value = errorText(error, "删除失败")
    ElMessage.error(operationError.value)
  } finally {
    if (componentAlive) deletingIds.value.delete(id)
  }
}

onMounted(reload)
onBeforeUnmount(() => {
  componentAlive = false
  requestSequence += 1
  deletingIds.value.clear()
  updatingModelIds.value.clear()
  updatingUrlIds.value.clear()
  for (const id of Object.keys(modelDrafts)) delete modelDrafts[id]
  for (const id of Object.keys(urlDrafts)) delete urlDrafts[id]
})
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
.token-form :deep(.el-autocomplete) { width: 100%; }
.field-help { width: 100%; margin: 5px 0 0; color: var(--ta-faint); font-size: 9px; line-height: 1.45; }
.target-audit-option { min-width: 0; }
.target-audit-control { display: flex; width: 100%; min-height: 48px; align-items: center; justify-content: space-between; gap: 16px; padding: 8px 10px; background: var(--ta-code); border: 1px solid var(--ta-line); border-radius: 4px; }
.target-audit-control strong { color: var(--ta-text); font-size: 11px; font-weight: 600; }
.target-audit-control p { margin: 3px 0 0; color: var(--ta-faint); font-size: 9px; line-height: 1.45; }
.target-audit-control :deep(.el-switch) { flex: 0 0 auto; }
.target-model-field { grid-column: 1 / -1; }
.target-model-field :deep(.el-autocomplete) { max-width: calc(50% - 6px); }
.inline-error { grid-column: 1 / -1; margin-bottom: 10px; padding: 8px 10px; color: var(--ta-danger); background: rgba(255, 125, 121, .055); border: 1px solid rgba(255, 125, 121, .2); border-radius: 4px; font-size: 11px; }
.form-actions { display: flex; grid-column: 1 / -1; gap: 8px; padding-top: 1px; }
.form-actions :deep(.el-button) { margin-left: 0; }
.state-panel { display: flex; gap: 12px; min-height: 190px; padding: 24px; color: var(--ta-muted); }
.state-prompt { color: var(--ta-green); }
.state-panel--error .state-prompt, .state-panel--error strong { color: var(--ta-danger); }
.state-panel strong { color: var(--ta-text); font-size: 12px; font-weight: 550; }
.state-panel p { margin: 5px 0 11px; color: var(--ta-faint); font-size: 10px; }
.table-scroll { overflow-x: auto; }
.compact-table { min-width: 1320px; }
.compact-table :deep(.el-table__cell) { padding: 8px 0; }
.compact-table :deep(.cell) { font-size: 11px; }
.token-masked { color: var(--ta-green); font-size: 10px; white-space: nowrap; }
.url-cell { display: grid; gap: 4px; min-width: 285px; padding: 4px 0; }
.url-cell :deep(.el-input__inner) { font-family: var(--ta-mono); font-size: 10px; }
.url-cell :deep(.el-input-group__append) { padding: 0 10px; background: rgba(78, 228, 174, .06); }
.url-hint { color: var(--ta-faint); font-family: var(--ta-mono); font-size: 8px; }
.model-cell { display: grid; gap: 4px; min-width: 240px; padding: 4px 0; }
.model-cell :deep(.el-autocomplete) { width: 100%; }
.model-save-state { color: var(--ta-green); font-family: var(--ta-mono); font-size: 9px; }
.target-state { color: var(--ta-faint); font-family: var(--ta-mono); font-size: 9px; }
.target-state--on { color: var(--ta-green); }
.delete-button { color: var(--ta-danger) !important; background: rgba(255, 125, 121, .045) !important; border-color: rgba(255, 125, 121, .22) !important; }
.delete-button:hover, .delete-button:focus-visible { background: rgba(255, 125, 121, .1) !important; border-color: rgba(255, 125, 121, .42) !important; }
@media (max-width: 900px) { .workspace-grid { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .page-heading { align-items: flex-start; } .token-form { grid-template-columns: 1fr; } .target-model-field :deep(.el-autocomplete) { max-width: 100%; } .form-actions :deep(.el-button) { flex: 1; } }
</style>
