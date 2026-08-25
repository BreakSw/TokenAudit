# TokenAudit 深度审计 RAG：首批模型知识源候选

> 版本：v1 · 搜索日期：2026-08-23
> 状态：仅供人工审查，尚未抓取、切分、Embedding 或写入向量库。

## 搜索与分级约定

- 本轮使用公开搜索结果和官方域名限定查询，没有调用项目 `.env` 中的 SerpAPI。
- 本轮没有批量爬取网页正文，只记录搜索得到的候选 URL，并对少量 URL 做可达性检查。
- `P0`：厂商官方、能够直接约束 Ground Truth 的模型说明、Model Card、System Card 或 API 模型文档。
- `P1`：厂商官方发布说明、官方技术说明或一线云平台的型号目录，用于补充发布时间、部署方式和边界。
- `P2`：独立评测、研究机构或可信技术媒体，用于交叉验证性能数据，不单独决定 Ground Truth。
- `P3`：社区资料、百科或综合解读，只用于别名发现和争议线索，不参与高权重评分。
- `APPROVE`：精确型号和两条 P0 基本成立，可进入下一轮正文审查。
- `CONDITIONAL`：型号大概率成立，但至少一条 P0 是动态目录或家族级资料，需人工打开确认精确型号。
- `HOLD`：没有找到精确型号的官方证据，暂缓入库。

## 1. GPT-5.6 Sol

状态：`APPROVE`

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | GPT-5.6 Sol Model · OpenAI API | https://developers.openai.com/api/docs/models/gpt-5.6-sol | 精确型号的官方 API 模型页，优先提取上下文、能力、接口与限制。 |
| P0-2 | Previewing GPT-5.6 Sol | https://openai.com/index/previewing-gpt-5-6-sol/ | 精确型号的官方发布说明，用于能力定位和首发边界。 |
| P1 | GPT-5.6 System Card | https://deploymentsafety.openai.com/gpt-5-6 | 官方安全与部署材料，补充风险边界和评估方法。 |
| P2 | GPT-5.6 Sol · BenchLM | https://benchlm.ai/models/gpt-5-6-sol | 独立模型指标页，用于交叉核对速度、成本和基准数据。 |
| P3 | GPT-5.6 · Wikipedia | https://en.wikipedia.org/wiki/GPT-5.6 | 家族级时间线和别名线索；只做导航，不用于最终判分。 |

## 2. GPT-5.6 Terra

状态：`APPROVE`

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | GPT-5.6 Terra Model · OpenAI API | https://developers.openai.com/api/docs/models/gpt-5.6-terra | 精确型号的官方 API 模型页。 |
| P0-2 | GPT-5.6：Frontier intelligence | https://openai.com/index/gpt-5-6/ | 官方家族发布页，包含 Sol、Terra、Luna 的定位关系。 |
| P1 | Advancing the price-performance frontier with GPT-5.6 | https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/ | 官方补充材料，重点用于 Terra 的成本、吞吐和使用边界。 |
| P2 | GPT-5.6 Terra · Artificial Analysis | https://artificialanalysis.ai/models/gpt-5-6-terra | 独立性能、速度和价格交叉验证。 |
| P3 | Sol vs Terra 开发者讨论 · OpenAI Community | https://community.openai.com/t/gpt-5-6-sol-vs-terra-what-are-you-seeing-in-real-development-during-these-first-days/1386726/6 | 真实使用差异线索；仅作为待验证 Claim 的来源。 |

## 3. GPT-5.6 Luna

状态：`APPROVE`

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | GPT-5.6 Luna Model · OpenAI API | https://developers.openai.com/api/docs/models/gpt-5.6-luna | 精确型号的官方 API 模型页。 |
| P0-2 | GPT-5.6：Frontier intelligence | https://openai.com/index/gpt-5-6/ | 官方家族页，用于确认 Luna 在三档模型中的定位。 |
| P1 | GPT-5.6 in ChatGPT · OpenAI Help | https://help.openai.com/en/articles/20001325-a-preview-of-gpt-56-sol-terra-and-luna | 官方产品侧说明，用于补充可用性和产品行为。 |
| P2 | GPT-5.6 Luna · Artificial Analysis | https://artificialanalysis.ai/models/gpt-5-6-luna | 独立性能和延迟交叉验证。 |
| P3 | GPT-5.6 Sol/Terra/Luna 解读 · AI総研 | https://www.ai-souken.com/article/what-is-gpt-5-6 | 第三方综合解读，只用于发现对比维度。 |

## 4. Claude Opus 4.6

状态：`CONDITIONAL`

> 精确名称能出现在独立模型目录中，但公开搜索没有稳定返回一条标题明确写着“Claude Opus 4.6”的 Anthropic 发布页。P0-1 和 P0-2 是动态官方目录，审查时必须确认页面当前确实包含 `Opus 4.6`，否则改为 `HOLD`。

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | Claude Opus · Anthropic | https://www.anthropic.com/claude/opus | 官方 Opus 产品页；需要人工确认当前版本标识是否为 4.6。 |
| P0-2 | Claude models overview · Anthropic | https://platform.claude.com/docs/en/about-claude/models/overview | 官方模型目录；用于确认精确 API ID、上下文和生命周期。 |
| P1 | Amazon Bedrock model IDs | https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html | 一线云平台型号目录，可交叉确认 Anthropic 精确部署 ID。 |
| P2 | Claude Opus 4.6 · Artificial Analysis | https://artificialanalysis.ai/models/claude-opus-4-6 | 独立模型指标候选；只有在官方型号确认后才可入库。 |
| P3 | Claude · Wikipedia | https://en.wikipedia.org/wiki/Claude_(AI) | 家族时间线和别名线索，不用于能力判分。 |

## 5. Claude Fable 5

状态：`APPROVE`

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | Claude Fable · Anthropic | https://www.anthropic.com/claude/fable | 精确产品线的官方模型页。 |
| P0-2 | Introducing Claude Fable 5 and Claude Mythos 5 · Claude Docs | https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5 | 官方精确型号介绍，适合抽取能力、限制和模型 ID。 |
| P1 | Claude Fable 5 and Claude Mythos 5 · Anthropic Research | https://www.anthropic.com/research/claude-fable-5-mythos-5 | 官方研究/发布材料，用于技术背景和评测依据。 |
| P2 | Claude Fable 5 · Artificial Analysis | https://artificialanalysis.ai/models/claude-fable-5 | 独立速度、价格和质量指标候选。 |
| P3 | Claude Fable 5 解读 · JAPAN AI | https://japan-ai.co.jp/media/7250/ | 第三方使用解读，只用于补充测试维度和争议点。 |

## 6. DeepSeek-V4-Pro

状态：`APPROVE`

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | DeepSeek-V4-Pro model card · DeepSeek AI | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro | 官方组织发布的精确 Model Card 候选。 |
| P0-2 | DeepSeek-V4-Pro GA Release · DeepSeek API Docs | https://api-docs.deepseek.com/news/news260813/ | 官方精确型号发布说明，可确认日期、API 行为和版本。 |
| P1 | DeepSeek Platform | https://platform.deepseek.com/ | 官方 API 平台，用于交叉确认当前可调用模型与价格。 |
| P2 | DeepSeek Releases V4 Pro · Forbes | https://www.forbes.com/sites/jonmarkman/2026/08/18/deepseek-releases-v4-pro-at-14x-the-price-of-its-cheapest-model/ | 技术媒体的发布时间和商业定位交叉证据。 |
| P3 | DeepSeek-V4-Pro · AI Release Tracker | https://aireleasetracker.com/model/deepseek/deepseek-v4-pro | 第三方规格汇总，只作为差异和待核验 Claim 线索。 |

## 7. Kimi K3

状态：`APPROVE`

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | Kimi K3 Quickstart · Kimi API Platform | https://platform.kimi.ai/docs/guide/kimi-k3-quickstart | 精确型号的官方 API 快速开始和调用约束。 |
| P0-2 | MoonshotAI/Kimi-K3 · GitHub | https://github.com/MoonshotAI/Kimi-K3 | 官方组织仓库，适合提取 Model Card、推理方式和部署信息。 |
| P1 | Kimi K3 model page | https://www.kimi.ai/ai-models/kimi-k3 | 官方产品/发布页，用于能力定位和官方基准。 |
| P2 | Kimi K3 · Artificial Analysis | https://artificialanalysis.ai/models/kimi-k3 | 独立性能、成本和速度交叉验证。 |
| P3 | Kimi K3 · OpenLM.ai | https://openlm.ai/kimi-k3/ | 社区规格和生态线索，不直接用于高置信度评分。 |

## 8. Grok 5

状态：`HOLD`

> 截至本次搜索，xAI 官方搜索结果仍以 Grok 4 / 4.x 为主，没有找到标题和型号均精确匹配 `Grok 5` 的官方模型页、API 文档或发布公告。下面五条仅用于确认型号是否出现，不能作为 Grok 5 的正式知识库源。

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | xAI model catalog | https://docs.x.ai/docs/models | 官方模型目录；人工审查是否已经出现 Grok 5 精确 API ID。 |
| P0-2 | Grok · xAI | https://x.ai/grok | 官方产品页；人工审查是否已更新到 Grok 5。 |
| P1 | Grok 4 announcement · xAI | https://x.ai/news/grok-4 | 目前能稳定检索到的最近官方家族基线，不是 Grok 5 证据。 |
| P2 | Artificial Analysis model index | https://artificialanalysis.ai/models | 检查是否有独立 Grok 5 条目；本轮猜测的精确路径返回 404。 |
| P3 | Grok · Wikipedia | https://en.wikipedia.org/wiki/Grok_(chatbot) | 家族时间线线索；只用于确认是否已经公开发布。 |

## 9. GLM-5.3

状态：`APPROVE`

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | GLM-5.3 · 智谱开放文档 | https://docs.bigmodel.cn/cn/guide/models/text/glm-5.3 | 精确型号官方文档，适合提取 API、上下文和能力限制。 |
| P0-2 | GLM-5.3 Overview · Z.AI Docs | https://docs.z.ai/guides/llm/glm-5.3 | 官方英文模型说明，便于与中文文档交叉核对。 |
| P1 | GLM-5.3: Frontier Coding with Emergent Cyber Capabilities | https://z.ai/blog/glm-5.3 | 官方发布和技术说明，适合提取官方评测与安全边界。 |
| P2 | GLM-5.3 报道 · InfoQ | https://www.infoq.cn/article/xWyWwu4ZNptlhpb15tia | 可信技术媒体的外部评测和发布信息交叉验证。 |
| P3 | GLM-5.3 · DataLearner | https://www.datalearner.com/ai-models/pretrained-models/glm-5-3 | 第三方规格汇总，只用于发现待核实能力点。 |

## 10. Qwen3-Max

状态：`CONDITIONAL`

> 两条 P0 是阿里云百炼的动态模型目录/API 文档，人工审查时必须确认正文包含精确模型 ID `qwen3-max`。Qwen3 技术报告主要覆盖家族，不应自动视为 Max 版本的专属事实。

| 等级 | 候选文本 | 链接 | 选择理由 |
|---|---|---|---|
| P0-1 | Model Studio model list · Alibaba Cloud | https://www.alibabacloud.com/help/en/model-studio/models | 官方模型目录，用于确认精确 API ID、上下文、价格和生命周期。 |
| P0-2 | Qwen API reference · Alibaba Cloud | https://www.alibabacloud.com/help/en/model-studio/qwen-api-reference | 官方 API 文档，用于结构化输出、工具调用和参数约束。 |
| P1 | Qwen3 official announcement | https://qwen.ai/blog?id=qwen3 | 官方家族技术和发布背景；只抽取能明确映射到 Max 的内容。 |
| P2 | Qwen3-Max · Artificial Analysis | https://artificialanalysis.ai/models/qwen3-max | 独立质量、速度和成本指标候选。 |
| P3 | Qwen3-Max · BenchLM | https://benchlm.ai/models/qwen3-max | 社区模型指标汇总，用于发现差异，不直接作为评分真值。 |

## 审查结论与入库闸门

| 模型 | 当前建议 | 进入正文审查的条件 |
|---|---|---|
| GPT-5.6 Sol | APPROVE | 核对模型页与 System Card 的版本日期。 |
| GPT-5.6 Terra | APPROVE | 确认价格性能页面中的 Terra 专属段落。 |
| GPT-5.6 Luna | APPROVE | 确认 Help Center 与 API 模型页的产品/API 差异。 |
| Claude Opus 4.6 | CONDITIONAL | 官方模型目录必须出现精确名称和 API ID。 |
| Claude Fable 5 | APPROVE | 核对官方 Docs 与 Research 页是否描述同一版本。 |
| DeepSeek-V4-Pro | APPROVE | 核对 Model Card 与 GA 公告的版本号是否一致。 |
| Kimi K3 | APPROVE | 核对 `.com` 与 `.ai` 平台文档是否属于同一官方版本。 |
| Grok 5 | HOLD | 必须找到 xAI 精确官方模型页或 API ID 后再选源。 |
| GLM-5.3 | APPROVE | 核对中英文官方文档的参数和版本日期。 |
| Qwen3-Max | CONDITIONAL | 阿里云官方目录必须明确出现 `qwen3-max`。 |

审查通过前，不执行网页抓取、不创建 Claim、不生成 Embedding，也不写入 Qdrant。
