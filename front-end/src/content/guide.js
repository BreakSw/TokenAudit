export const GUIDE_SECTIONS = [
  {
    id: "overview",
    title: "工作流概览",
    keywords: "快速开始 配置 Token 预检 并行 审计 报告"
  },
  {
    id: "requirements",
    title: "运行要求",
    keywords: "Node.js npm Java Maven Python Redis 依赖 安装"
  },
  {
    id: "configure",
    title: "系统与 Redis",
    keywords: ".env 环境变量 VITE_BACKEND_BASE_URL Redis B01 database 1 并发 队列 超时"
  },
  {
    id: "audit-ai",
    title: "配置审计 AI",
    keywords: "设置 审计 AI API Key 服务商 模型 URL 有效期 Redis 加密"
  },
  {
    id: "start",
    title: "启动项目",
    keywords: "npm Vite 5173 Spring Boot Maven 8086 python -m audit_core"
  },
  {
    id: "token",
    title: "录入 Token",
    keywords: "POST /api/tokens Base URL 中转站 OpenRouter AiHubMix 平台 声称模型 model"
  },
  {
    id: "models",
    title: "选择与修改模型",
    keywords: "PUT /api/tokens/{id}/model 下拉 输入 模型 ID 声称模型 自定义"
  },
  {
    id: "run-audit",
    title: "预检与发起审计",
    keywords: "POST /api/audits preflight auditId 六个维度 连通性 鉴权"
  },
  {
    id: "parallel",
    title: "并行与终止任务",
    keywords: "POST /api/audits/{id}/cancel 并发 队列 queued active cancelled 终止"
  },
  {
    id: "events",
    title: "读取实时事件",
    keywords: "GET /api/audits/{id}/events progress pipeline preflight event"
  },
  {
    id: "report",
    title: "查看报告",
    keywords: "GET /api/audits/{id} executionState Markdown JSON Excel PDF 风险 历史"
  },
  {
    id: "security",
    title: "密钥与安全边界",
    keywords: "BACKEND_API_KEY X-API-KEY 加密 私网 SSRF API Key .env"
  },
  {
    id: "errors",
    title: "常见错误",
    keywords: "401 403 503 Network Error Model Not Exist audit_queue_full preflight timeout python 排查"
  }
]

export function searchGuideSections(query) {
  const normalized = String(query || "").trim().toLowerCase()
  if (!normalized) return GUIDE_SECTIONS

  return GUIDE_SECTIONS.filter((section) =>
    `${section.title} ${section.keywords}`.toLowerCase().includes(normalized)
  )
}
