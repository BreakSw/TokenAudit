# 暗色安全控制台验收记录

验收日期：2026-08-08

## 范围

- 暗色控制台应用外壳与首页
- 实时审计工作流
- Token 管理与历史记录
- API 平台式使用文档
- 审计报告控制台
- 前后端默认配置与审计核心调度

## 自动化验证

### 前端

- `npm test`
  - 15 个测试文件通过
  - 96 项测试通过
  - 覆盖应用外壳、路由、首页、文档、滚动浮现、存储容错、API 客户端、实时审计、Token、历史和报告页
- `npm run build`
  - Vite 生产构建通过
  - 存在既有的大 chunk 警告：主 JavaScript 产物约 1.1 MB，后续可通过路由懒加载和拆分 Element Plus 优化

### Python 审计核心

- `python -m unittest discover -s audit-core/tests -v`
  - LangGraph 动态状态回归测试通过
- `python -m compileall -q audit-core/audit_core`
  - 全部 Python 模块编译检查通过
- 手工最小调度验证返回 `{'a': 1, 'b': 2}`，不再返回 `None`

### Java 后端

- `mvn clean package`
  - Java 17 release 编译通过
  - Maven 测试阶段通过（当前仓库尚无 Java 测试源码）
  - Spring Boot repackage 通过，JAR 可通过 `java -jar` 启动
- 启动打包产物后验证：
  - `GET /api/agents/health` 返回 `{"status":"ok"}`
  - `GET /api/tokens` 返回 HTTP 200 与 `application/json`

## 报告页专项验证

- 六个审计维度按有效性、权限、模型真实性、合规、稳定性、安全性的 canonical 顺序展示
- 综合结论、风险警示、使用建议、Markdown、原始 JSON、事件流和导出路径均有独立区域
- Markdown 通过 Vue 文本插值写入 `pre`，不使用 `v-html`
- running 状态自动轮询，completed/failed 停止
- 同一报告的并发刷新会合并
- 切换报告 ID 后，旧响应无法覆盖新报告
- 组件卸载后，待完成请求不会继续加载事件、写状态或弹出错误消息
- 所有主要报告区块使用一次性 `v-reveal` 与 70ms 递增 stagger

## 可视化验收说明

曾启动本地 Vite 服务并尝试使用应用内浏览器进行逐页与响应式检查。浏览器此前停留在连接失败的内部错误页，恢复导航时被浏览器安全策略阻止，因此本轮未完成基于截图的桌面/320/375/390/768px 人工视觉验收。相关响应式规则、reduced-motion 样式和键盘焦点样式已由源码检查确认；正式发布前仍建议在真实浏览器补做一轮视觉走查。

## 已知剩余风险

- Token 当前在 SQLite 中明文保存，需要单独设计密钥管理、历史数据迁移与密钥轮换
- 每次审计创建 daemon 线程和 Python 子进程，缺少并发上限、队列背压与进程级超时
- CORS 允许所有来源、方法和请求头，部署到非本机环境前应按实际前端域名收紧
- Java 后端尚无正式自动化测试
- 前端主包较大，首屏网络性能仍有优化空间
