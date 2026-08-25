# Claude Fable 5 RAG 效果测试

- 初检 Top-K：12
- Rerank 保留：5
- 向量语义 Top-1：100.0%
- Rerank 语义 Top-1：100.0%
- 审计属性 Recall@5：100.0%
- 审计属性 MRR：0.7778

## 用例

### fallback_disambiguation

- 查询：如何区分 Fable 5 官方回退到 Opus 4.8 与中转站偷偷替换模型？
- 向量 Top-1：`attr-fable5-fallback-disambiguation`
- Rerank Top-1：`attr-fable5-fallback-disambiguation`
- 目标审计属性排名：1

### adaptive_thinking

- 查询：Claude Fable 5 能不能关闭 thinking，应该用什么参数控制推理深度？
- 向量 Top-1：`fable5-adaptive-thinking`
- Rerank Top-1：`fable5-adaptive-thinking`
- 目标审计属性排名：3

### tool_capabilities

- 查询：Fable 5 有哪些能够区分普通模型的复杂工具与 Agent 能力？
- 向量 Top-1：`attr-fable5-tools`
- Rerank Top-1：`attr-fable5-tools`
- 目标审计属性排名：1
