export const AUDIT_STAGES = [
  {
    key: "validity",
    label: "有效性",
    detail: "验证 Token 和宣称模型是否可用"
  },
  {
    key: "permission",
    label: "权限",
    detail: "验证宣称模型、可选目标模型和匿名调用"
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

export const DEEP_AUDIT_STAGES = [
  {
    key: "rag_retrieval",
    label: "双库检索",
    detail: "并行检索官方规格与模型行为证据"
  },
  {
    key: "ground_truth",
    label: "基线整理",
    detail: "由审计者 Agent 区分硬事实与软行为特征"
  },
  {
    key: "probe_design",
    label: "动态出题",
    detail: "根据当前轮次和证据缺口生成新母题"
  },
  {
    key: "fuzz_execute",
    label: "模糊执行",
    detail: "每题生成三个变体并并行调用目标模型"
  },
  {
    key: "parallel_judging",
    label: "并行裁判",
    detail: "语义、行为差分与一致性 Judge 同时判定"
  },
  {
    key: "red_team",
    label: "反方复核",
    detail: "排查路由、截断、提示改写等替代解释"
  },
  {
    key: "final_decision",
    label: "综合结论",
    detail: "锁定确定性分数并生成可追溯结论"
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
