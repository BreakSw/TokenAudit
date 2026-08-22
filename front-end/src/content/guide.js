export const GUIDE_SECTIONS = [
  {
    id: "requirements",
    title: "运行要求",
    keywords: "Node.js npm Java Maven Python 依赖 安装"
  },
  {
    id: "configure",
    title: "配置环境变量",
    keywords: ".env VITE_BACKEND_BASE_URL Redis 审计 AI API Key 模型 URL 有效期"
  },
  {
    id: "start",
    title: "启动项目",
    keywords: "npm Vite 5173 Spring Boot Maven 8086 python -m audit_core"
  },
  {
    id: "token",
    title: "录入 Token",
    keywords: "POST /api/tokens Base URL 平台 声称模型 非声称模型 model"
  },
  {
    id: "run-audit",
    title: "发起审计",
    keywords: "POST /api/audits GET /api/audits/{id}/events auditId 事件 六个维度"
  },
  {
    id: "report",
    title: "查看报告",
    keywords: "GET /api/audits/{id} Markdown JSON Excel PDF 风险 历史"
  },
  {
    id: "errors",
    title: "常见错误",
    keywords: "401 403 503 Model Not Exist python X-API-KEY 排查"
  }
]

export function searchGuideSections(query) {
  const normalized = String(query || "").trim().toLowerCase()
  if (!normalized) return GUIDE_SECTIONS

  return GUIDE_SECTIONS.filter((section) =>
    `${section.title} ${section.keywords}`.toLowerCase().includes(normalized)
  )
}
