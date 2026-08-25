# TokenAudit 模型知识源原始快照

本目录保存首批 10 个目标模型的 50 个候选来源。采集阶段只负责取得正文、记录来源和检查技术可用性，尚未进行知识切块、Claim 提取、Embedding、Rerank 或写入 Qdrant。

## 总体结果

- 模型：10 个；
- 候选来源：50 篇；
- Firecrawl 技术采集成功：50 篇；
- 正文总字符数：1,757,068；
- 纯正文中明确出现目标型号全名：34 篇；
- 所有来源均保存独立 `metadata.json` 和 SHA-256；
- Firecrawl 每分钟 10 次的限制已通过 6.5 秒请求间隔解决。

| 模型 | 原审核状态 | 技术成功 | 正文明示型号 | 正文字符数 | 目录 |
|---|---|---:|---:|---:|---|
| GPT-5.6 Sol | APPROVE | 5/5 | 5/5 | 262,308 | `gpt-5.6-sol/` |
| GPT-5.6 Terra | APPROVE | 5/5 | 2/5 | 91,795 | `gpt-5.6-terra/` |
| GPT-5.6 Luna | APPROVE | 5/5 | 4/5 | 222,805 | `gpt-5.6-luna/` |
| Claude Opus 4.6 | CONDITIONAL | 5/5 | 3/5 | 199,747 | `claude-opus-4.6/` |
| Claude Fable 5 | APPROVE | 5/5 | 5/5 | 99,495 | `claude-fable-5/` |
| DeepSeek-V4-Pro | APPROVE | 5/5 | 3/5 | 44,715 | `deepseek-v4-pro/` |
| Kimi K3 | APPROVE | 5/5 | 5/5 | 196,257 | `kimi-k3/` |
| Grok 5 | HOLD | 5/5 | 0/5 | 398,248 | `grok-5/` |
| GLM-5.3 | APPROVE | 5/5 | 5/5 | 75,676 | `glm-5.3/` |
| Qwen3-Max | CONDITIONAL | 5/5 | 2/5 | 166,022 | `qwen3-max/` |

“技术成功”只代表页面返回 200 且存在足够长度的正文；“正文明示型号”是在排除本项目自动写入的 YAML 元数据后，对正文做的精确型号匹配。家族级页面可能不写完整型号，因此 0 次命中不是自动删除条件，但必须进入人工语义审查。

## 重点风险

### Grok 5 继续保持 HOLD

五个候选来源均成功抓取，但正文都没有出现 `Grok 5`。浏览器对 xAI 模型目录的独立抓取也得到 0 次命中，因此现有材料只能作为 Grok 家族/Grok 4 的背景资料，不能证明 Grok 5 已经形成可审计的官方 Ground Truth。

### CONDITIONAL 型号

- Claude Opus 4.6：官方模型总览和 AWS 型号目录正文未明确出现完整型号；
- Qwen3-Max：两篇官方 API/模型总览及 Qwen3 家族发布页未明确出现完整型号；
- 这些页面可用于接口边界和家族行为，但型号专属 Claim 必须来自明确命中的文本片段。

### APPROVE 但需要降权的来源

- GPT-5.6 Terra 的家族发布页、价格性能页和社区讨论没有在正文中完整写出 `GPT-5.6 Terra`；
- GPT-5.6 Luna 的家族发布页没有完整写出目标型号；
- DeepSeek Platform 首页和 Forbes 页面没有完整写出 `DeepSeek-V4-Pro`；
- 上述来源暂不删除，但后续切块时不得把无型号归属的段落直接绑定到目标模型。

## 目录约定

每个模型包含两篇 P0，以及 P1/P2/P3 各一篇。每个来源目录包含：

- `content.md`：Firecrawl 正文和可追溯 YAML 元数据；
- `metadata.json`：HTTP 状态、最终 URL、正文长度和 SHA-256；
- 模型根目录的 `capture-report.json`：该模型五个来源的机器可读汇总；
- 少数高风险来源包含 `browser-capture.md`，作为浏览器渲染交叉验证结果。

来源的 P0-P3 等级是权威性先验，不是最终事实置信度。后续必须结合“型号归属、发布日期、版本适用范围、可复现性和对掺水检测的区分度”重新评分。
