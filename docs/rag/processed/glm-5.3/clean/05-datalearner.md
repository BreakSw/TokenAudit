模型参数
7533.3亿
上下文长度
1M
中文支持
支持
推理能力
智谱 AI / Z.ai 于 2026 年 8 月 14 日发布的开放权重编程与网络安全模型。沿用 GLM-5.2 的 7533.3 亿参数 MoE 基座，能力提升来自继续扩展后训练与强化学习算力而非更换基座；1M 上下文、128K 最大输出，始终启用思考且 reasoning_effort 默认 max。在 DataLearner 已收录数据中，HLE 62.50 排 181 个模型第 3，Terminal-Bench 2.1 88.20 排 44 个第 3，CyberGym、ExploitBench、AutomationBench、SWE-Marathon、PostTrain Bench 五项排第 1。权重计划在额外安全评估后约两周公开。
数据优先来自官方发布（GitHub、Hugging Face、论文），其次为评测基准官方结果，最后为第三方评测机构数据。 了解数据收集方法
GLM-5.3
模型基本信息
推理过程
支持
思考模式
思考水平 · 最高 (Max) (默认)思考水平 · 低 (Low)思考水平 · 高 (High)
上下文长度
1M tokens
最大输出长度
128K tokens
模型类型
推理大模型
输入/输出模态
文本 → 文本
发布时间
2026-08-14
模型文件大小
暂无数据
MoE架构
总参数 / 激活参数
7533.3亿 / 不涉及
知识截止
暂无数据
GLM-5.3
开源和体验地址
代码开源状态
暂无数据
预训练权重开源
暂无数据
GitHub 源码
暂无GitHub开源地址
Hugging Face
暂无开源HuggingFace地址
在线体验
https://zcode.z.ai
GLM-5.3
官方介绍与博客
官方论文
GLM-5.3: Frontier Coding with Emergent Cyber Capabilities
DataLearnerAI博客
暂无介绍博客
GLM-5.3
API接口信息
接口速度
5/5
暂无公开的 API 定价信息。
GLM-5.3
评测结果
GLM-5.3 当前已收录的代表性评测结果包括 HLE（3 / 181，得分 62.50）、Terminal-Bench 2.1（3 / 44，得分 88.20）、AutomationBench（1 / 8，得分 48.20）。 本页还汇总了参数规模、上下文长度与 API 价格，便于结合评测结果与部署约束一起判断模型适配度。
思考模式
全部思考
综合评估
共 1 项评测
评测名称 / 模式
得分
排名/总数
HLE
最高工具
62.50
3 / 181
AI Agent - 工具使用
共 8 项评测
评测名称 / 模式
得分
排名/总数
ExploitGym (6h)
最高工具
130
1 / 1
ExploitGym (2h)
最高工具
105
1 / 1
Terminal-Bench 2.1
最高工具
88.20
3 / 44
CyberGym
最高工具
84.50
1 / 3
Toolathlon-Verified
最高工具
73
3 / 5
ExploitBench
最高工具
54.40
1 / 1
AutomationBench
最高工具
48.20
1 / 8
Terminal-Bench 3.0
最高工具
28.30
3 / 6
编程与软件工程
共 6 项评测
评测名称 / 模式
得分
排名/总数
FrontierSWE
最高工具
78.10
2 / 4
DeepSWE
最高工具
66.90
8 / 27
NL2Repo-Bench
最高工具
58
2 / 8
SWE-Marathon
最高工具
42.50
1 / 4
PostTrain Bench
最高工具
39.80
1 / 4
Program Bench
最高工具
19
5 / 5
Agent能力评测
共 1 项评测
评测名称 / 模式
得分
排名/总数
Agents' Last Exam
最高工具
28.50
4 / 11
生产力知识
共 1 项评测
评测名称 / 模式
得分
排名/总数
GDPval-AA v2
最高工具
1769
2 / 13
查看评测深度分析 与其他模型对比
GLM-5.3
模型关系
查看 GLM-5.3 的前代版本、竞品与其他直接关联模型，继续了解产品演进和同类选择。
前代版本
前代版本GLM-5.2
前代版本GLM 5.1
前代版本GLM-5
前代版本GLM-4.7
竞品模型
竞品模型Kimi K3
竞品模型Claude Opus 5
竞品模型GPT-5.6 Sol
竞品模型DeepSeek-V4-Pro
和其他模型对比
同期模型GLM-5.3 vs Kimi K311个评测
前代版本GLM-5.3 vs GLM-5.28个评测
同期模型GLM-5.3 vs DeepSeek-V4-Pro8个评测
同期模型GLM-5.3 vs GPT-5.6 Sol5个评测
同期模型GLM-5.3 vs Claude Opus 54个评测
想自定义其他组合？ 打开对比工具
GLM-5.3
发布机构
智谱AI
智谱AI
查看发布机构详情
GLM-5.3
模型解读
GLM-5.3 是智谱 AI / Z.ai 于 2026 年 8 月 14 日正式发布的 GLM-5 系列开放权重模型，面向复杂 Coding、长程 Agent 任务和网络安全工作。官方说明它与 GLM-5.2 使用同一基座，能力提升全部来自过去一个月继续扩展后训练环境、任务多样性和强化学习算力，而不是更换预训练基座。
架构与规格
由于官方明确 GLM-5.3 沿用 GLM-5.2 基座，本条目按同一约 753.33B 参数的 MoE / DSA 基座记录；官方尚未单独披露 GLM-5.3 的激活参数规模。GLM-5.3 继续使用 GLM-5.2 建立的长上下文与后训练栈，包括用于长上下文处理的 IndexShare、面向长程任务强化学习的 SAO，以及大规模异步训练框架 slime。官方评测在多项长程任务中使用 1M context，并将最大输出设为 128K，因此 DataLearner 记录其上下文窗口为 1M、最大输出为 128K。模型输入与输出均为文本。
思考模式与 API 变化
官方模型 ID 为 glm-5.3。模型始终启用 thinking，不再支持 thinking.type=disabled；reasoning_effort 支持 low、high、max 三档，默认值为 max，官方也建议 Coding 任务使用 max。迁移自旧模型时，如果原请求关闭了 thinking，需要先改为 enabled 并选择至少 low 档，否则请求会失败。
官方评测
Z.ai 发布页给出了覆盖 Coding、Cyber 和 Agentic 三组的完整对比表。GLM-5.3 的 Coding 成绩包括 Terminal-Bench 2.1 88.2、Terminal-Bench 3.0 28.3、DeepSWE v1.1 66.9、NL2Repo 58.0、ProgramBench 19.0、FrontierSWE 78.1、SWE-Marathon v1.1 42.5、PostTrainBench 39.8；Cyber 成绩包括 CyberGym 84.5、ExploitGym 在 2 小时与 6 小时预算下分别完成 105 和 130 个实例、ExploitBench 54.4；Agentic 成绩包括 Toolathlon Verified 73.0、AutomationBench v1.0.6 48.2、Agents' Last Exam 28.5、HLE with Tools 62.5、GDPval-AA v2 1769。
这些数字是官方发布评测，不代表所有部署、采样参数或第三方服务都能复现相同结果。官方脚注显示，多数 Agent / Cyber 测试使用 Claude Code 2.1.207、max reasoning effort 和受控工具环境；不同基准还采用了 300K、400K 或 1M context、不同超时和重复运行口径。DataLearner 将它们统一挂在“Max（工具）”评测模式下，并在基准定义与本页正文保留测试条件。
网络安全能力与开放权重状态
官方把 GLM-5.3 定位为面向 Coding 的开放权重模型，并在发布页的 Open Source 章节说明：由于网络安全能力具有双重用途，将在完成额外安全评估与加固后，于发布约两周后公开权重。因此，把 GLM-5.3 概括为闭源并不准确；更精确的当前状态是 开放权重已官宣，权重包与具体许可证待发布。截至 2026 年 8 月 14 日，官方 Hugging Face 尚无 GLM-5.3 权重仓库，GLM-5 系列 GitHub 仓库也尚未列出 5.3 支持。DataLearner 不再把它标成“不开源”，但在权重及许可证实际上线前也不预先套用 GLM-5.2 的 MIT License。
访问与计费
GLM-5.3 已向全部 GLM Coding Plan 用户开放，并可在 ZCode、Claude Code、OpenCode 等 Coding Agent 中使用。Coding Plan 采用积分制：每 10,000 tokens 的输入、缓存输入和输出分别使用 6.9、1.7、24 的积分乘数；工作日 14:00–18:00（UTC+8）之外按标准积分的 50% 计算。Z.ai 的标准按量 API 价格页在发布时尚未列出 GLM-5.3 的每百万 token 美元价格，因此 DataLearner 暂不生成按量 API 价格行，避免把订阅积分误写成货币价格。
官方来源
GLM-5.3: Frontier Coding with Emergent Cyber Capabilities
GLM Coding Plan 官方说明
Z.ai 标准 API 价格页
Z.ai 官方 Hugging Face
GLM-5 系列 GitHub 仓库
GLM-5.3
常见问题
GLM-5.3 和 GLM-5.2 是同一个基座吗？升级在哪里？
是同一个基座。官方明确 GLM-5.3 沿用 GLM-5.2 的约 7533.3 亿参数 MoE / DSA 基座，没有更换预训练底座，能力提升全部来自过去一个月继续扩展后训练环境、任务多样性和强化学习算力。因此本站按同一参数规模记录，官方尚未单独披露 GLM-5.3 的激活参数量。
GLM-5.3 的权重什么时候开源？
官方表示权重计划在完成额外安全评估后约两周公开。由于 GLM-5.3 强化了网络安全方向的能力（ExploitGym、ExploitBench、CyberGym 等），开放权重前的安全评估比常规版本更谨慎。
GLM-5.3 还能关闭思考模式吗？
不能。官方模型 ID 为 glm-5.3，模型始终启用 thinking，不再支持 thinking.type=disabled。reasoning_effort 提供 low、high、max 三档，默认值是 max，官方也建议编程任务直接用 max。从旧模型迁移时如果原请求显式关闭了思考，需要改写调用参数。
GLM-5.3 在网络安全类评测上表现如何？
这是它区别于同系列其他版本的地方。在 DataLearner 已收录的数据里，CyberGym 84.50 在 3 个模型中排第 1，ExploitBench 54.40、ExploitGym（2h）105 分和（6h）130 分均为当前唯一收录成绩，AutomationBench 48.20 在 8 个模型中排第 1。这组成绩说明它的定位不只是通用编程模型。
GLM-5.3 的编程能力和第一梯队差多少？
分任务看差异明显。仓库级长程任务表现突出：SWE-Marathon 42.50 和 PostTrain Bench 39.80 均排第 1，NL2Repo-Bench 58 排 8 个模型第 2，FrontierSWE 78.10 排第 2。但 Program Bench 19 分在 5 个模型中垫底，DeepSWE 66.90 在 27 个模型中排第 8——短程算法题和高难度仓库补丁上仍不是最强。
GLM-5.3 的上下文和最大输出是多少？
上下文窗口 1M tokens，最大输出 128K tokens。官方评测在多项长程任务中就是按 1M 上下文跑的。模型输入与输出均为纯文本，不支持图像或音频输入。
DataLearner 官方微信
欢迎关注 DataLearner 官方微信，获得最新 AI 技术推送
DataLearner 官方微信二维码
