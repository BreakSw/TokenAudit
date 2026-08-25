# Claude Fable 5 Milvus 自审报告

- 集合：`tokenaudit_knowledge_v2`
- 数据位置：`E:\Desktop\TokenAudit\TokenAudit\.worktrees\dark-cyber-frontend\data\milvus\tokenaudit.db`
- 记录：22 / 预期 22
- 重复内容哈希：0
- 违规隔离记录：0
- 六组检索 Top-1 命中：1/6
- 六组语义 Top-1 命中：6/6
- 审计属性 Recall@5：6/6

## 检索结果

- 查询：安全分类器触发时 Claude Fable 5 API 返回什么状态码和 stop_reason？
  - 期望：`attr-fable5-refusal-protocol`
  - Top-1：`fable5-refusal-protocol`
  - 相似度：0.788287
  - 期望审计属性排名：2
- 查询：Claude Fable 5 能否关闭思考，应该怎样控制推理深度？
  - 期望：`attr-fable5-adaptive-thinking`
  - Top-1：`fable5-adaptive-thinking`
  - 相似度：0.788299
  - 期望审计属性排名：3
- 查询：Claude Fable 5 会不会返回原始思维链？
  - 期望：`attr-fable5-thinking-visibility`
  - Top-1：`fable5-thinking-visibility`
  - 相似度：0.763097
  - 期望审计属性排名：3
- 查询：如何区分 Fable 5 官方回退到 Opus 4.8 与中转站偷偷换模型？
  - 期望：`attr-fable5-fallback-disambiguation`
  - Top-1：`attr-fable5-fallback-disambiguation`
  - 相似度：0.581902
  - 期望审计属性排名：1
- 查询：Fable 5 支持哪些复杂工具和 Agent 能力？
  - 期望：`attr-fable5-tools`
  - Top-1：`fable5-supported-features`
  - 相似度：0.58259
  - 期望审计属性排名：3
- 查询：Fable 5 的上下文窗口和最大输出 Token 是多少？
  - 期望：`attr-fable5-context-output`
  - Top-1：`fable5-context-output`
  - 相似度：0.644705
  - 期望审计属性排名：4

## 尚未入库

- 带 Opus 4.8 fallback 的 Artificial Analysis 指标；
- 未人工校验的官方 Benchmark 图片；
- 官方营销评价和客户证言；
- 日语二手 Benchmark 数字；
- 价格、促销和数据保留等非模型行为信息。

## 判断

只有 Claim 与审计属性进入集合，原始网页章节没有直接 Embedding。数据库可用于下一阶段检索实验，但在加入对照模型和完成 Benchmark 图片校验前，不应作为最终模型真实性判决的唯一依据。
