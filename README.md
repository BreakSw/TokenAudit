# TokenAudit（简单的骨架）

TokenAudit 是一个「Token 审计工具」示例项目：前端（Vue3 + Element Plus）负责录入 Token / 发起审计 / 展示报告与进度；后端（Spring Boot + MyBatis + SQLite + Redis）负责持久化与调度；审计核心（Python 多 Agent）负责对中转平台 Token 做多维审计，并通过用户配置的 OpenAI 兼容审计 AI 做判定与汇总。

目前审计的核心流程还是静态，正在开发中（后续会加入多agent动态合作，RAG 模型特性知识检索，Harness engineering等新技术）

## 功能概览

- Token 管理：录入/删除中转平台 Token（后端 SQLite 持久化）
- 一键审计：有效性 / 权限 / 模型真实性 / 合规 / 稳定性 / 安全性（6 项）
- 真实进度：后端实时采集 Python 多 Agent 事件流（phase/token_call/deepseek_call），前端展示进度条与审计过程
- 报告导出：JSON / Markdown / Excel / PDF（PDF 可选，缺字体会跳过）

## 项目结构

```text
TokenAudit/
  front-end/        # Vue3 + ElementPlus 前端
  back-end/         # Spring Boot 后端（SQLite + MyBatis）
  audit-core/       # Python 多Agent 审计核心（python -m audit_core）
  data/
    database/       # SQLite 数据库（运行后生成）
    report/         # 审计报告导出目录（运行后生成）
  .env.example      # 环境变量模板（不放密钥）
  .gitignore
```

## 环境准备（必需）

- Node.js 18+（用于前端）
- Java 17+（后端 `pom.xml` 目标版本是 17）
- Maven 3.8+
- Python 3.9+（建议 3.10/3.11 也可）

建议先确认命令可用：

```bash
node -v
npm -v
java -version
mvn -v
python --version
```

## 第一步：配置环境变量（Redis / Python / 路径）

### 1) 创建 `.env`（推荐方式）

在项目根目录复制一份模板：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`，确认 Redis 连接信息：

```properties
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DATABASE=1
```

审计 AI 不再固定为 DeepSeek。服务启动后，在前端右上角进入“设置 → 审计判定模型”，填写服务商、完整 Chat Completions URL、模型、API Key 和有效期。API Key 会加密保存至 Redis，每次保存都会重新计算 TTL。

### 2) Python 可执行文件与审计核心目录

后端会启动 Python 子进程执行审计（`python -m audit_core`）。如果你的环境里 `python` 不在 PATH，需要在 `.env` 里指定：

```properties
PYTHON_EXECUTABLE=python
AUDIT_CORE_WORKDIR=../audit-core
```

Windows 常见两种情况：
- 你有 Python Launcher：`PYTHON_EXECUTABLE=py`
- 你只有 python.exe：`PYTHON_EXECUTABLE=python`

### 3) 后端接口 API Key（可选）

如果你想给后端接口加一层简单防护，可配置：

```properties
BACKEND_API_KEY=自定义字符串
```

前端会把你在页面右上角输入的 key 放到请求头 `X-API-KEY`。

## 第二步：安装并运行 Python 审计核心（audit-core）

进入 `audit-core` 安装依赖：

```bash
cd audit-core
pip install -r requirements.txt
```

如果你使用虚拟环境（推荐）：

```bash
cd audit-core
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

审计核心的入口是：

```bash
python -m audit_core
```

它从 stdin 读取 JSON 配置并输出 JSON 报告；同时会把审计进度事件以 JSON 行写到 stderr，供后端实时采集。

## 第三步：启动后端（Spring Boot）

后端默认端口：`8086`（可在 [application.yml](file:///e:/Desktop/Group_Projects/Personal_Projects/TokenAudit/back-end/src/main/resources/application.yml) 修改）

启动：

```bash
cd back-end
mvn spring-boot:run
```

健康检查：

```bash
curl http://localhost:8086/api/agents/health
```

首次启动会在 `data/database/` 下创建 SQLite 数据库，并按 `schema.sql` 建表。

## 第四步：启动前端（Vue3 + Vite）

前端默认端口：`5173`（如果被占用，Vite 会自动尝试下一个端口）

```bash
cd front-end
npm install
npm run dev
```

前端默认后端地址由 `VITE_BACKEND_BASE_URL` 决定：
- 优先读取 `front-end/.env.development` 或你自己设置的 Vite 环境变量
- 若未配置，会用 `http://localhost:8086`

你当前项目默认是 `8086`，推荐确保 `front-end/.env.development` 中为：

```properties
VITE_BACKEND_BASE_URL=http://localhost:8086
```

## 使用教程（新手必看）

### 1) 先录入 Token（Token管理）

在前端进入「Token管理」，新增 Token 时字段含义如下：

- 名称：随便填，用于展示（例如：`小马-claude-opus`）
- Token：中转站给你的 key（敏感信息，谨慎保存）
- 中转平台：展示用（例如：`小马中转`）
- API 地址：可填基础地址，也可填完整的 OpenAI 兼容推理端点
  - 基础地址：`https://api.xiaoma.best/v1`
  - 完整端点：`https://api.xiaoma.best/v1/chat/completions`
  - 非标准路径的中转站建议填写完整端点，系统不会按平台名称改写地址
- 宣称模型：中转站返回的 `model`（例如：`claude-opus-4-6`）
- 目标模型审计：默认关闭；仅当 Token 理应受模型白名单限制时开启
- 目标审计模型：开启后必填，用于验证模型权限边界（例如：`gpt-4o-mini`）；支持多模型的中转站通常保持关闭

### 2) 发起审计（发起审计）

选择 Token 与导出格式后点击「开始审计」：

- 页面会显示实时进度条与当前阶段（有效性/权限/掺水/合规/稳定/综合）
- 下方“审计过程”会实时展示事件流（token_call/deepseek_call），用于定位卡在哪一步或失败原因

### 3) 查看报告（报告页 / 历史记录）

- 历史记录可以按 `auditId` 查看报告
- 报告页支持 Markdown + JSON 展示，并可复制 Markdown
- 导出文件默认写入 `data/report/`

## API 接口（后端）

基础路径：`http://localhost:8086`

- Token
  - `GET /api/tokens` 列表
  - `POST /api/tokens` 新增
  - `DELETE /api/tokens/{id}` 删除
- Audit
  - `POST /api/audits` 发起审计（异步，立即返回 `auditId`）
  - `GET /api/audits/{id}` 获取审计状态/进度/报告
- `GET /api/audits/{id}/events` 获取事件流（真实进度）
  - `GET /api/audits` 审计历史列表
- Health
  - `GET /api/agents/health`

## 常见问题排查（Troubleshooting）

### 1) `audit_ai_not_configured`

说明审计 AI 配置不存在或已过期：

- 在前端打开“设置 → 审计判定模型”并重新保存配置
- 检查 Redis 是否运行、连接信息是否正确

### 2) 审计 AI 返回 `Model Not Exist`

说明设置中的模型不存在或当前账号不可用：

- 在服务商控制台查询当前 API Key 可用的模型列表
- 回到“设置 → 审计判定模型”修改模型并保存，无需重启后端

### 3) 审计“秒失败”，事件里有 `Cannot run program "python"`

说明后端找不到 Python：

- Windows 可尝试 `.env` 设置：`PYTHON_EXECUTABLE=py`
- 或确保 `python` 已加入 PATH

### 4) 前端端口冲突

Vite 会提示 “Port XXXX is in use, trying another one...”，属于正常行为；看控制台输出的最终 Local 地址即可。

### 5) PDF 导出失败

PDF 依赖字体文件，未配置会跳过或失败。可通过环境变量指定字体：

```properties
AUDIT_PDF_FONT_TTF=你本机字体文件路径.ttf
```

## 安全提示

- 不要把任何 API Key 写入 `.env.example` 或提交到仓库；审计 API Key 请通过设置界面保存
- `.env` 已被 `.gitignore` 忽略，专用于本地/服务器部署
- Token 属于敏感信息，建议使用最小权限、开启限流/白名单（如中转站支持）

## 生产部署建议（可选）

前端构建静态文件：

```bash
cd front-end
npm run build
```

后端打包：

```bash
cd back-end
mvn -DskipTests package
```

然后用 `java -jar back-end/target/token-audit-backend-0.1.0.jar` 启动后端，并在服务器上配置 `.env`。
