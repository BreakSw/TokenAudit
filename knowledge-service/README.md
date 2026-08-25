# TokenAudit Knowledge Service

该服务把模型资料转换为可追溯的 Evidence Chunk、原子 Claim 和审计属性，使用
Voyage 生成向量后写入项目内的 Milvus Lite 数据库。未经验证的 OCR、P2/P3 二手
信息、来源不匹配内容和 fallback 污染数据不会直接成为 Ground Truth。

## 当前数据

- 数据库：`data/milvus/tokenaudit.db/`
- 当前集合：`tokenaudit_knowledge_v3`
- 保留的旧集合：`tokenaudit_knowledge_v2`（仅 Fable 5，22 条）
- 当前集合记录：175 条
- 有合格向量数据的模型：8 个
- 因来源不匹配暂未入库：Grok 5、Qwen3-Max

运行环境、缓存和 OCR 工具仍位于 D 盘，业务数据全部位于项目目录：

```text
D:\DOWNload\TokenAuditRuntime\env
D:\DOWNload\TokenAuditRuntime\pip-cache
D:\DOWNload\TokenAuditRuntime\temp
D:\DOWNload\TokenAuditRuntime\hf-cache
D:\DOWNload\TokenAuditRuntime\torch-cache
D:\download\OCR\tesseract.exe
<project>\data\milvus\tokenaudit.db
```

Milvus Lite 的 `tokenaudit.db` 是数据库目录，不是普通 SQLite 文件，不要直接修改
其中的 Parquet、向量索引、WAL、manifest 或 schema 文件。

## 数据处理流程

```text
抓取后的 Markdown
  → Unstructured 元素解析与网页去噪
  → Unstructured 表格解析
  → 图片下载
  → Unstructured hi_res / ocr_only + Tesseract OCR
  → Unstructured chunk_by_title
  → LlamaIndex 精确去重并合并来源
  → 目标模型正文匹配
  → P0/P1 Claim 准入与证据链验证
  → 审计属性编译
  → Voyage voyage-code-3 Embedding
  → Milvus COSINE 混合检索 Top-12
  → Voyage rerank-2.5 保留 Top-5
```

### 分块策略

```text
max_characters=1800
new_after_n_chars=1200
combine_text_under_n_chars=300
overlap=120
overlap_all=false
isolate_table=true
```

标题是优先语义边界；短元素在同一标题内合并，超过 1200 字符后允许产生新块，
1800 字符为硬上限。只有被迫切开的长块保留 120 字符重叠，表格独立成块并保存
Unstructured 的结构结果。

### Ground Truth 准入

多模型通用管线遵守以下规则：

1. 网页正文必须明确出现目标模型，front matter 中的人工标签不算证据。
2. 事实正文必须来自 P0/P1；P2/P3 只用于审查和隔离。
3. Claim 必须指向一个证据 Chunk；标题和规格落在相邻 Chunk 时，同时保留主体确认 Chunk。
4. HOLD 来源、目标模型不匹配、fallback 污染和编码严重损坏的数据不得入库。
5. 审计属性必须回链到 Claim、Evidence Chunk、原始文件、URL 和抓取时间。
6. 图片 OCR 默认隔离，未经人工复核不会参与 Embedding。

## 执行

项目根目录为当前 PowerShell 工作目录：

```powershell
$env:PYTHONPATH = (Resolve-Path '.\knowledge-service').Path
$env:HF_HOME = 'D:\DOWNload\TokenAuditRuntime\hf-cache'
$env:TORCH_HOME = 'D:\DOWNload\TokenAuditRuntime\torch-cache'
$env:TEMP = 'D:\DOWNload\TokenAuditRuntime\temp'
$env:TMP = 'D:\DOWNload\TokenAuditRuntime\temp'
```

完整处理、OCR、Embedding 并重建当前集合：

```powershell
D:\DOWNload\TokenAuditRuntime\env\Scripts\python.exe `
  -m tokenaudit_knowledge.cli ingest-all-models `
  --env-file E:\Desktop\TokenAudit\.env `
  --env-file D:\DOWNload\TokenAuditRuntime\milvus.env `
  --rebuild
```

若文本、OCR 和处理产物已存在，只重新生成向量与 Milvus：

```powershell
$env:VOYAGE_MIN_REQUEST_INTERVAL_SECONDS = '21'
D:\DOWNload\TokenAuditRuntime\env\Scripts\python.exe `
  -m tokenaudit_knowledge.cli ingest-all-models `
  --env-file E:\Desktop\TokenAudit\.env `
  --env-file D:\DOWNload\TokenAuditRuntime\milvus.env `
  --rebuild --reuse-processed
```

运行混合检索 Demo：

```powershell
$env:VOYAGE_MIN_REQUEST_INTERVAL_SECONDS = '21'
D:\DOWNload\TokenAuditRuntime\env\Scripts\python.exe `
  .\knowledge-service\scripts\test_mixed_rag.py `
  --env-file E:\Desktop\TokenAudit\.env `
  --env-file D:\DOWNload\TokenAuditRuntime\milvus.env
```

免费 Voyage 账户为 3 RPM / 10K TPM。客户端会按字符预算拆分 Embedding，并对
HTTP 429 自动退避；`VOYAGE_MIN_REQUEST_INTERVAL_SECONDS=21` 用于主动遵守该限制。

## 产物

每个模型的处理目录：

```text
docs/rag/processed/<model-id>/
├── clean/
├── elements.jsonl
├── chunks.jsonl
├── evidence-chunks.jsonl
├── tables.jsonl
├── claims.jsonl
├── ground-truth-claims.jsonl
├── attributes.jsonl
├── assets.jsonl
├── quarantine.json
└── processing-manifest.json
```

多模型合并结果：

```text
docs/rag/processed/all-models/
├── combined-records.jsonl
├── combined-processing-manifest.json
├── milvus-export.jsonl
├── mixed-rag-test-results.json
├── mixed-rag-test.log
└── mixed-rag-report.md
```

`data/milvus/` 被 Git 忽略；可读 JSONL、清单和报告保存在 `docs/rag/processed/`。
所有 API Key 只从本地环境文件读取，不会写入处理产物或报告。
