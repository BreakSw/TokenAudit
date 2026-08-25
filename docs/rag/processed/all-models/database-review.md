# 多模型 Milvus 数据库自审

## 结论

`tokenaudit_knowledge_v3` 已成功写入项目内的 Milvus Lite 数据库，可作为当前多模型
RAG 集合使用。旧的 `tokenaudit_knowledge_v2` 仍然保留，未被删除。

## 完整性

- 集合行数：175
- Evidence Chunk：44
- Claim：67
- Audit Attribute：64
- 模型数量：8 个有合格记录，2 个只有隔离产物
- 重复 ID：0
- 重复内容哈希：0
- 非准入记录误入：0
- fallback 污染记录误入：0
- 向量模型：Voyage `voyage-code-3`
- 向量维度：1024
- 距离指标：COSINE

## 模型分布

| 模型 | 记录数 | 来源状态 | 结论 |
|---|---:|---|---|
| claude-fable-5 | 22 | APPROVE | 保留原有高质量专用规则记录 |
| claude-opus-4.6 | 20 | CONDITIONAL | 已入库；官方页面混有后续 Opus 版本，使用时保留条件标记 |
| deepseek-v4-pro | 19 | APPROVE | 已入库 |
| glm-5.3 | 27 | APPROVE | 已入库 |
| gpt-5.6-luna | 16 | APPROVE | 已入库 |
| gpt-5.6-sol | 26 | APPROVE | 已入库 |
| gpt-5.6-terra | 16 | APPROVE | 已入库 |
| kimi-k3 | 29 | APPROVE | 已入库 |
| grok-5 | 0 | HOLD | 官方正文未出现 Grok 5，不制造 Ground Truth |
| qwen3-max | 0 | CONDITIONAL | P0/P1 正文不含 Qwen3-Max，暂不入库 |

## Unstructured 图片与 OCR

- 发现图片引用：460
- 成功下载：190
- OCR 返回文本：128
- OCR 空结果：4
- Fable 5 明确跳过的装饰图片：39

所有 OCR 和图片结果均保存在各模型的 `assets.jsonl` 与 `assets/` 目录。它们默认处于
隔离状态，未参与本次 175 条 Ground Truth Embedding。

## 检索评测

- 混合问题：17
- Vector Top-1 Accuracy：100.0%
- Vector Recall@12：100.0%
- Vector MRR@12：1.0000
- Vector nDCG@12：0.9144
- Rerank Top-1 Accuracy：100.0%
- Rerank Recall@5：100.0%
- Rerank MRR@5：1.0000
- Rerank nDCG@5：0.8526
- 目标模型 Top-1 Accuracy：100.0%
- 精确审计属性 Recall@5：100.0%

Rerank nDCG 低于 Vector nDCG 的主要原因是候选从 12 条压缩为 5 条，同一问题的多条
相关 Claim/Evidence 被裁掉；Top-1、Recall 与 MRR 没有下降。

## 风险

这组问题由已准入审计属性构造，适合验证管线和跨模型混检是否工作，不是独立盲测。
100% 指标不能直接解释为真实 Token 审计准确率。下一阶段应增加人工编写、与入库文本
措辞不同的对抗查询，并为 Grok 5、Qwen3-Max 补充真正包含目标模型的官方 P0/P1 来源。
