<template>
  <el-row :gutter="16" class="page-grid">
    <el-col :span="10" class="left-col">
      <el-card>
        <template #header>
          <div class="card-header">
            <div>
              <div class="card-title">新增Token</div>
              <div class="card-subtitle">Token会保存到后端SQLite，用于审计调用与历史追溯，请妥善保管</div>
            </div>
          </div>
        </template>

        <el-collapse v-model="openGuide" style="margin-bottom: 12px">
          <el-collapse-item name="guide" title="新手教程：怎么填这张表？">
            <el-alert
              type="info"
              show-icon
              :closable="false"
              title="字段填写规则"
              description="Base URL 只填域名根（例如 https://api.xiaoma.best），不要带 /v1/chat/completions；宣称模型填中转站返回的 model（例如 claude-opus-4-6）；非宣称模型用于越权测试，可先填 gpt-4o-mini。"
            />
            <el-alert
              style="margin-top: 10px"
              type="warning"
              show-icon
              :closable="false"
              title="安全建议"
              description="Token 属于敏感信息：避免截图/外发；建议使用专用Token；如中转站支持白名单/限流请开启。"
            />
          </el-collapse-item>
        </el-collapse>

        <el-form label-width="120px" class="form">
          <el-form-item label="名称">
            <el-input v-model="form.name" placeholder="例如：测试Token" />
          </el-form-item>
          <el-form-item label="Token">
            <el-input v-model="form.token" type="password" show-password />
          </el-form-item>
          <el-form-item label="中转平台">
            <el-input v-model="form.platform" placeholder="例如：某某平台" />
          </el-form-item>
          <el-form-item label="Base URL">
            <el-input v-model="form.tokenBaseUrl" placeholder="例如：https://xxx.com" />
          </el-form-item>
          <el-form-item label="宣称模型">
            <el-input v-model="form.claimedModel" placeholder="例如：gpt-4o" />
          </el-form-item>
          <el-form-item label="非宣称模型">
            <el-input v-model="form.nonClaimedModel" placeholder="例如：gpt-4o-mini" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="save">保存</el-button>
            <el-button @click="reset">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
    <el-col :span="14" class="right-col">
      <el-card>
        <template #header>
          <div class="card-header row">
            <div>
              <div class="card-title">Token列表</div>
              <div class="card-subtitle">选择一个Token后即可去“发起审计”页面执行审计</div>
            </div>
            <el-button @click="reload" :loading="loading">刷新</el-button>
          </div>
        </template>

        <div v-if="!loading && tokens.length === 0" class="empty-wrap">
          <el-empty description="暂无Token，请先在左侧新增" />
        </div>

        <el-table v-else :data="tokens" stripe style="width: 100%" height="520">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="tokenMasked" label="Token" width="160" />
          <el-table-column prop="platform" label="平台" width="140" />
          <el-table-column prop="claimedModel" label="宣称模型" width="160" />
          <el-table-column fixed="right" label="操作" width="120">
            <template #default="{ row }">
              <el-button type="danger" size="small" @click="remove(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { createToken, deleteToken, listTokens } from "../request/api"
import { isUrl, required } from "../utils/validate"

const tokens = ref([])
const loading = ref(false)
const saving = ref(false)
const openGuide = ref(["guide"])

const form = reactive({
  name: "",
  token: "",
  platform: "",
  tokenBaseUrl: "",
  claimedModel: "",
  nonClaimedModel: ""
})

function reset() {
  form.name = ""
  form.token = ""
  form.platform = ""
  form.tokenBaseUrl = ""
  form.claimedModel = ""
  form.nonClaimedModel = ""
}

async function reload() {
  loading.value = true
  try {
    tokens.value = await listTokens()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "加载失败")
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!required(form.name) || !required(form.token) || !required(form.platform) || !required(form.claimedModel) || !required(form.nonClaimedModel)) {
    ElMessage.warning("请补全必填项")
    return
  }
  if (!isUrl(form.tokenBaseUrl)) {
    ElMessage.warning("Base URL格式不正确")
    return
  }
  saving.value = true
  try {
    await createToken({ ...form })
    ElMessage.success("已保存")
    reset()
    await reload()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "保存失败")
  } finally {
    saving.value = false
  }
}

async function remove(id) {
  try {
    await ElMessageBox.confirm("确认删除该Token？", "提示", { type: "warning" })
  } catch {
    return
  }
  try {
    await deleteToken(id)
    ElMessage.success("已删除")
    await reload()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "删除失败")
  }
}

onMounted(reload)
</script>

<style scoped>
.page-grid {
  align-items: stretch;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.card-header.row {
  align-items: center;
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

.form {
  margin-top: 4px;
}

.empty-wrap {
  padding: 18px 0;
}

@media (max-width: 920px) {
  .left-col,
  .right-col {
    width: 100%;
  }
}
</style>
