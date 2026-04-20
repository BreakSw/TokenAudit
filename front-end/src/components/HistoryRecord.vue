<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <div>
          <div class="card-title">历史审计记录</div>
          <div class="card-subtitle">按审计ID可追溯完整报告（含证据）</div>
        </div>
        <el-button @click="reload" :loading="loading">刷新</el-button>
      </div>
    </template>

    <el-table :data="records" stripe style="width: 100%" height="560">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="tokenId" label="TokenID" width="100" />
      <el-table-column prop="auditTime" label="审计时间" width="180" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="进度" width="120">
        <template #default="{ row }">
          <el-progress :percentage="Number(row.progress || 0)" :stroke-width="8" />
        </template>
      </el-table-column>
      <el-table-column prop="overallConclusion" label="综合结论" />
      <el-table-column fixed="right" label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="open(row.id)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { listAudits } from "../request/api"

const router = useRouter()
const records = ref([])
const loading = ref(false)

async function reload() {
  loading.value = true
  try {
    records.value = await listAudits()
  } catch (e) {
    ElMessage.error(e?.response?.data?.error || e?.message || "加载失败")
  } finally {
    loading.value = false
  }
}

function open(id) {
  router.push(`/report/${id}`)
}

function statusType(status) {
  if (status === "completed") return "success"
  if (status === "running") return "warning"
  if (status === "failed") return "danger"
  return "info"
}

onMounted(reload)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
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
</style>
