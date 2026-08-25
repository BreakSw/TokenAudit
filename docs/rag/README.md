# RAG 数据位置

从现在开始，TokenAudit 的 RAG 业务数据统一保存在项目目录中。D 盘的
`TokenAuditRuntime` 只保留 Python 环境、依赖缓存、OCR 工具和无密钥运行配置。

## 数据目录

- 原始网页数据：`docs/rag/raw-sources/<model-id>/`
- 清洗、分块和审计处理结果：`docs/rag/processed/<model-id>/`
- Milvus Lite 数据库：`data/milvus/tokenaudit.db/`
- 当前多模型集合：`tokenaudit_knowledge_v3`
- 保留的 Fable 5 旧集合：`tokenaudit_knowledge_v2`

Milvus Lite 数据库是二进制目录，不适合直接用文本编辑器查看。需要人工检查时，
优先打开以下可读文件：

- `processed/all-models/milvus-export.jsonl`：多模型集合的完整可读导出
- `processed/all-models/combined-processing-manifest.json`：合并入库清单与模型覆盖情况
- `processed/all-models/mixed-rag-report.md`：混合 Top-K/Rerank 效果报告
- `processed/all-models/mixed-rag-test-results.json`：逐题结构化评测结果
- `processed/all-models/mixed-rag-test.log`：混合评测过程日志
- `processed/claude-fable-5/processing-manifest.json`：处理参数和产物清单

## 路径规则

Milvus 使用项目相对路径：

```dotenv
MILVUS_URI=./data/milvus/tokenaudit.db
```

程序会相对于当前项目根目录解析该路径，因此移动工作树或项目后不会继续向旧的
绝对路径写数据。

`data/milvus/` 默认不会提交到 Git，避免把本地数据库和大量二进制文件上传到仓库；
可读的处理产物保存在 `docs/rag/processed/`，便于检查和版本管理。
