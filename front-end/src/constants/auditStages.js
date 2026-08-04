export const AUDIT_STAGES = [
  {
    key: "validity",
    label: "有效性",
    detail: "验证 Token 和宣称模型是否可用"
  },
  {
    key: "permission",
    label: "权限",
    detail: "比较宣称模型、非宣称模型和匿名调用"
  },
  {
    key: "watering",
    label: "模型真实性",
    detail: "分析能力特征与模型声明是否一致"
  },
  {
    key: "compliance",
    label: "合规",
    detail: "检查敏感信息和异常调用风险"
  },
  {
    key: "stability",
    label: "稳定性",
    detail: "比较多次调用的一致性与耗时"
  },
  {
    key: "security",
    label: "安全性",
    detail: "检查 Token 结构与匿名访问风险"
  },
  {
    key: "overall",
    label: "综合判定",
    detail: "汇总 Agent 证据和风险建议"
  }
]

export function stageIndex(key) {
  const index = AUDIT_STAGES.findIndex((stage) => stage.key === key)
  return index === -1 ? 0 : index
}

export function stageLabel(key) {
  const stage = AUDIT_STAGES.find((item) => item.key === key)
  if (!stage) return "-"
  return stage.key === "overall" ? stage.label : `${stage.label}审计`
}
