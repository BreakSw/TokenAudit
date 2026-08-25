# TokenAudit 精选行为数据集 v1

该目录保存用于模型特征分析和审计题生成的 Hugging Face 精选样本。大仓库采用远程流式读取，项目中只保留抽样结果；当前数据文件合计约 94.75 MB。

| 模型 | 本地文件 | 保留记录 | 说明 |
|---|---|---:|---|
| Claude Fable 5 | `claude-fable-5/selected.jsonl` | 500 | 覆盖 60 个原始会话 |
| Claude Opus 4.6 | `claude-opus-4.6/selected.parquet` | 886 | 完整的小型高推理集合 |
| DeepSeek-V4-Pro | `deepseek-v4-pro/selected.jsonl` | 400 | 400 个独立 Agent 会话 |
| GLM-5.2 | `glm-5.2/selected.jsonl` | 1,556 | 来自 42 个 Benchmark 文件，同时保留通过与失败轨迹 |
| GPT-5.6 Luna | `gpt-5.6-luna/selected.jsonl` | 890 | Persona 注入蒸馏数据，不用于判定原生回答风格 |
| GPT-5.6 Sol | `gpt-5.6-sol/selected.jsonl` | 553 | 553 个独立轨迹，只保留最终完整上下文 |
| Kimi K3 | `kimi-k3/selected.parquet` | 1,163 | 覆盖 582 个独立轨迹 |
| GPT-5.6 Terra | 无 | 0 | 暂未发现可验证的公开样本 |

`manifest.json` 包含精确来源、抽样方式、文件大小和可信度说明。数据文件默认被 Git 忽略，避免把约 95 MB 的外部数据推送到代码仓库。

下载脚本：

```powershell
D:\DOWNload\TokenAuditRuntime\env\Scripts\python.exe `
  scripts\rag\download-hf-audit-subset.py `
  --output docs\rag\datasets\huggingface-selected-v1 `
  --temp-dir D:\DOWNload\TokenAuditRuntime\temp
```

校验脚本：

```powershell
D:\DOWNload\TokenAuditRuntime\env\Scripts\python.exe `
  scripts\rag\verify-hf-audit-subset.py `
  --root docs\rag\datasets\huggingface-selected-v1
```

公开数据中符合密钥格式的字符串已统一替换为 `<TOKENAUDIT_REDACTED_SECRET>`，实际值不会写入清单或校验输出。
