# 多模型混合 RAG 检索评测报告

- Milvus 集合：`tokenaudit_knowledge_v3`
- 入库记录：175
- 测试问题：17
- 向量初检 Top-K：12
- Voyage Rerank 保留：5

## 总体指标

- Vector Top-1 Accuracy：100.0%
- Vector Recall@12：100.0%
- Vector MRR@12：1.0000
- Vector nDCG@12：0.9144
- Vector 模型 Top-1 Accuracy：100.0%
- Rerank Top-1 Accuracy：100.0%
- Rerank Recall@5：100.0%
- Rerank MRR@5：1.0000
- Rerank nDCG@5：0.8526
- Rerank 模型 Top-1 Accuracy：100.0%
- 精确审计属性 Recall@5：100.0%

## 数据覆盖

| 模型 | 来源状态 | 入库记录 | Claim | 属性 | 覆盖缺口 |
|---|---:|---:|---:|---:|---|
| claude-fable-5 | APPROVE | 22 | 9 | 6 | 无硬性缺口 |
| claude-opus-4.6 | CONDITIONAL | 20 | 7 | 7 | Source manifest review status is CONDITIONAL. |
| deepseek-v4-pro | APPROVE | 19 | 7 | 7 | 无硬性缺口 |
| glm-5.3 | APPROVE | 27 | 10 | 10 | 无硬性缺口 |
| gpt-5.6-luna | APPROVE | 16 | 7 | 7 | 无硬性缺口 |
| gpt-5.6-sol | APPROVE | 26 | 10 | 10 | 无硬性缺口 |
| gpt-5.6-terra | APPROVE | 16 | 7 | 7 | 无硬性缺口 |
| grok-5 | HOLD | 0 | 0 | 0 | No captured page body explicitly names the target model; front matter was ignored.；No P0/P1 chunk explicitly names the target model.；Source manifest review status is HOLD. |
| kimi-k3 | APPROVE | 29 | 10 | 10 | 无硬性缺口 |
| qwen3-max | CONDITIONAL | 0 | 0 | 0 | No P0/P1 chunk explicitly names the target model.；Source manifest review status is CONDITIONAL. |

## 分模型指标

| 模型 | 问题数 | Vector Top-1 | Vector Recall | Rerank Top-1 | Rerank Recall |
|---|---:|---:|---:|---:|---:|
| claude-fable-5 | 3 | 100.0% | 100.0% | 100.0% | 100.0% |
| claude-opus-4.6 | 2 | 100.0% | 100.0% | 100.0% | 100.0% |
| deepseek-v4-pro | 2 | 100.0% | 100.0% | 100.0% | 100.0% |
| glm-5.3 | 2 | 100.0% | 100.0% | 100.0% | 100.0% |
| gpt-5.6-luna | 2 | 100.0% | 100.0% | 100.0% | 100.0% |
| gpt-5.6-sol | 2 | 100.0% | 100.0% | 100.0% | 100.0% |
| gpt-5.6-terra | 2 | 100.0% | 100.0% | 100.0% | 100.0% |
| kimi-k3 | 2 | 100.0% | 100.0% | 100.0% | 100.0% |

## 逐题结果

### claude-fable-5-fallback

- 查询：How can an audit distinguish Claude Fable 5's official Opus fallback from an unauthorized relay model substitution?
- Vector Top-1：`attr-fable5-fallback-disambiguation`
- Rerank Top-1：`attr-fable5-fallback-disambiguation`
- 目标属性排名：1

### claude-fable-5-reasoning

- 查询：Can Claude Fable 5 disable thinking, and which effort parameter controls its reasoning depth?
- Vector Top-1：`fable5-adaptive-thinking`
- Rerank Top-1：`fable5-adaptive-thinking`
- 目标属性排名：2

### claude-fable-5-tools

- 查询：Which complex tool and agent capabilities distinguish Claude Fable 5?
- Vector Top-1：`attr-fable5-tools`
- Rerank Top-1：`attr-fable5-tools`
- 目标属性排名：1

### claude-opus-4.6-context_output

- 查询：What context-window and maximum-output behavior should Claude Opus 4.6 exhibit?
- Vector Top-1：`attr-claude-opus-4.6-context_output`
- Rerank Top-1：`attr-claude-opus-4.6-context_output`
- 目标属性排名：1

### claude-opus-4.6-modalities

- 查询：Which input and output modalities are officially supported by Claude Opus 4.6?
- Vector Top-1：`attr-claude-opus-4.6-modalities`
- Rerank Top-1：`attr-claude-opus-4.6-modalities`
- 目标属性排名：1

### deepseek-v4-pro-reasoning_behavior

- 查询：Which reasoning modes and control parameters are characteristic of DeepSeek-V4-Pro?
- Vector Top-1：`attr-deepseek-v4-pro-reasoning_behavior`
- Rerank Top-1：`attr-deepseek-v4-pro-reasoning_behavior`
- 目标属性排名：1

### deepseek-v4-pro-context_output

- 查询：What context-window and maximum-output behavior should DeepSeek-V4-Pro exhibit?
- Vector Top-1：`attr-deepseek-v4-pro-context_output`
- Rerank Top-1：`attr-deepseek-v4-pro-context_output`
- 目标属性排名：1

### glm-5.3-reasoning_behavior

- 查询：Which reasoning modes and control parameters are characteristic of GLM-5.3?
- Vector Top-1：`attr-glm-5.3-reasoning_behavior`
- Rerank Top-1：`attr-glm-5.3-reasoning_behavior`
- 目标属性排名：1

### glm-5.3-context_output

- 查询：What context-window and maximum-output behavior should GLM-5.3 exhibit?
- Vector Top-1：`attr-glm-5.3-context_output`
- Rerank Top-1：`attr-glm-5.3-context_output`
- 目标属性排名：1

### gpt-5.6-luna-reasoning_behavior

- 查询：Which reasoning modes and control parameters are characteristic of GPT-5.6 Luna?
- Vector Top-1：`attr-gpt-5.6-luna-reasoning_behavior`
- Rerank Top-1：`attr-gpt-5.6-luna-reasoning_behavior`
- 目标属性排名：1

### gpt-5.6-luna-context_output

- 查询：What context-window and maximum-output behavior should GPT-5.6 Luna exhibit?
- Vector Top-1：`attr-gpt-5.6-luna-context_output`
- Rerank Top-1：`attr-gpt-5.6-luna-context_output`
- 目标属性排名：1

### gpt-5.6-sol-reasoning_behavior

- 查询：Which reasoning modes and control parameters are characteristic of GPT-5.6 Sol?
- Vector Top-1：`attr-gpt-5.6-sol-reasoning_behavior`
- Rerank Top-1：`attr-gpt-5.6-sol-reasoning_behavior`
- 目标属性排名：1

### gpt-5.6-sol-context_output

- 查询：What context-window and maximum-output behavior should GPT-5.6 Sol exhibit?
- Vector Top-1：`attr-gpt-5.6-sol-context_output`
- Rerank Top-1：`attr-gpt-5.6-sol-context_output`
- 目标属性排名：1

### gpt-5.6-terra-reasoning_behavior

- 查询：Which reasoning modes and control parameters are characteristic of GPT-5.6 Terra?
- Vector Top-1：`attr-gpt-5.6-terra-reasoning_behavior`
- Rerank Top-1：`attr-gpt-5.6-terra-reasoning_behavior`
- 目标属性排名：1

### gpt-5.6-terra-context_output

- 查询：What context-window and maximum-output behavior should GPT-5.6 Terra exhibit?
- Vector Top-1：`attr-gpt-5.6-terra-context_output`
- Rerank Top-1：`attr-gpt-5.6-terra-context_output`
- 目标属性排名：1

### kimi-k3-reasoning_behavior

- 查询：Which reasoning modes and control parameters are characteristic of Kimi K3?
- Vector Top-1：`attr-kimi-k3-reasoning_behavior`
- Rerank Top-1：`attr-kimi-k3-reasoning_behavior`
- 目标属性排名：1

### kimi-k3-context_output

- 查询：What context-window and maximum-output behavior should Kimi K3 exhibit?
- Vector Top-1：`attr-kimi-k3-context_output`
- Rerank Top-1：`attr-kimi-k3-context_output`
- 目标属性排名：1

## 局限

- The evaluation set is deterministic and derived from admitted source-backed attributes; it is a smoke test, not an independent benchmark.
- Models with HOLD or mismatched source bodies are excluded from scored queries rather than assigned fabricated Ground Truth.
- A successful retrieval result validates this corpus and query set, not the authenticity of any relay model by itself.
