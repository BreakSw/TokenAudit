# GPT-5.6 Sol 原始资料快照

本目录保存 GPT-5.6 Sol 第一批候选知识源的抓取结果。当前阶段只完成正文采集和技术可用性检查，**尚未进行切块、事实提取、Embedding、Rerank 或写入 Qdrant**。

## 采集结果

| 等级 | 来源 | Firecrawl | 源站状态 | Markdown 字符数 | 本地目录 |
|---|---|---:|---:|---:|---|
| P0 | OpenAI API 模型页 | 成功 | 200 | 6,309 | `p0/01-openai-model-page/` |
| P0 | OpenAI 发布说明 | 成功 | 200 | 33,467 | `p0/02-openai-release/` |
| P1 | OpenAI System Card | 成功 | 200 | 160,251 | `p1/03-openai-system-card/` |
| P2 | BenchLM 模型页 | 成功 | 200 | 24,356 | `p2/04-benchlm/` |
| P3 | Wikipedia 条目 | 成功 | 200 | 37,925 | `p3/05-wikipedia/` |

每个来源目录包含：

- `content.md`：Firecrawl 提取的正文，带采集来源、时间和内容哈希；
- `metadata.json`：请求地址、最终地址、HTTP 状态、正文长度、SHA-256 和技术验收状态；
- 第一篇 P0 额外包含 `browser-capture.md`，用于验证浏览器渲染结果与 Firecrawl 结果是否指向同一有效页面。

根目录的 `capture-report.json` 是五个来源的机器可读汇总。

## 当前验收含义

`acceptedForReview=true` 只说明页面可访问、返回非错误状态且抓到了足够长度的正文，不代表其中每一项模型宣称都已被 TokenAudit 接受为 Ground Truth。

- P0/P1 后续仍需检查型号、版本日期、评测设置和适用范围；
- P2 仅用于构造独立性能对照，不应覆盖官方硬约束；
- P3 只用于发现别名、争议和待验证线索；
- System Card 体量较大，后续应按章节和评测表格进行结构感知切分，不能直接按固定字符数粗切。
