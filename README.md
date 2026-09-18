# 社媒监测洞察系统（数字能源社媒）

面向华为数字能源 Marketing 团队的**内部社媒监测洞察系统**：基于「极致了数据 / dajiala」付费 API 抓取微信公众号内容，结合大模型做正文/评论分析，支持定时任务、阅读排名与删除待确认队列。

> ⚠️ **仅供内部使用**。抓取数据不对外分发；通过 dajiala 官方付费 Key 合规调用。上线前请过法务/合规。

---

## 功能总览

| 模块 | 说明 |
|------|------|
| 多账户登录 | RBAC 管理员/成员；默认 `Admin / Seek22626301`（首登强制改密） |
| 公众号管理 | 批量导入（名称/微信号/链接，自动检索校验去重）、在线检索添加、**分组管理**（CRUD/批量分配/按组筛选）、标签、监测开关 |
| 内容抓取 | 选账号/**按分组** + 时间段 + **点选字段**（标题/发布时间/正文/阅读/点赞/在看/转发/收藏/评论），字段方案可存模板，后台任务带进度、可取消、**可删除** |
| 数据持久化 | SQLite(WAL) 起步，可平滑切 PostgreSQL/MySQL；指标采用**快照只增不删**模型，天然支持自动覆盖与趋势曲线 |
| 一键导出 | 文章/评论/分析结果导出 Excel/CSV（浏览器下载 + 服务器导出目录） |
| 智能分析 | 分析框架（模块+维度+提示词模板）支持**保存/导入/导出 JSON**；维度可增删改、启停、**临时 Prompt 维度**（仅本次运行）；分析对象三种：正文/评论/**聚合**（把一批文章作为整体提炼议题，按议题精确汇总总阅读/总点赞——LLM 只负责归类，数字代码算）；内容三入口：文章库多选（跨页保留）/ 一键导入抓取任务 / 粘贴自定义文本 |
| 待确认队列 | 文章被删 / 评论异常下降时**不覆盖旧值**，进待确认队列，人工决定「保留原始」或「确认删除」 |
| 数据源 Key 池 | dajiala 多 Key，按用户绑定、用量/配额统计、失败切换 |
| 定时任务 | cron 定时抓取 + 按阅读量排名（日报/周报） |
| MCP / 云服务 | MCP server（如 FireCrawl）、LightPanda、Tavily 的**配置 + 凭证管理 + 连通性测试** |

> **预留扩展（M3，不在首版）**：视频号抓取、FireCrawl/LightPanda/Tavily 全网/定点热词检索 —— 已通过 `SourceProvider` 接口预留插拔点，不改主流程。

---

## 技术栈

- **后端**：Python 3.13 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · PyJWT/bcrypt/Fernet · APScheduler · httpx
- **前端**：Vue 3 · Vite · Element Plus · Pinia · Vue Router · ECharts
- **数据库**：SQLite（默认，WAL）→ 可切 PostgreSQL/MySQL
- **部署**：Docker + docker-compose（nginx 托管前端并反代后端）

## 项目结构

```
数字能源社媒/
├── backend/app/
│   ├── core/         # config / security(JWT,bcrypt,Fernet) / deps / logging
│   ├── db/           # engine, session(WAL), init+seed(默认Admin)
│   ├── models/       # 全部 SQLAlchemy 表
│   ├── schemas/      # Pydantic
│   ├── api/v1/       # REST 路由
│   ├── providers/    # SourceProvider ABC + dajiala + mock + registry(预留 shipinhao/firecrawl/...)
│   ├── llm/          # OpenAI 兼容 client + 注册
│   ├── analyzers/    # 分析引擎 + 维度执行器
│   ├── mcpclient/    # MCP client(stdio/sse/http)
│   ├── services/     # 业务逻辑（fetch/analysis/key/ranking/review/export...）
│   └── tasks/        # 进程内任务队列 + APScheduler + 排名
├── frontend/src/     # api / views / layout / router / store
├── deploy/           # backend.Dockerfile / frontend.Dockerfile / docker-compose.yml / nginx.conf / deploy.sh / update.sh
├── docs/
└── data/             # 运行时生成：monitor.db + exports/（Docker 卷挂载）
```

---

## 快速开始

### 方式 A：本地开发（无 Docker）

```bash
# 1. 后端
cd backend
python -m venv ../.venv && source ../.venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
# 回到项目根，准备 .env（本地调试可先 PROVIDER_MOCK=true 用 Mock 数据源）
cp ../.env.example ../.env
uvicorn app.main:app --reload --port 8000

# 2. 前端（另开终端）
cd frontend
npm install
npm run dev        # http://localhost:5173 ，已配置代理 /api → 8000
```

浏览器打开 `http://localhost:5173`，用 `Admin / Seek22626301` 登录（首登提示改密）。

### 方式 B：Docker 一键部署（云服务器）

```bash
bash deploy/deploy.sh     # 检查依赖、生成 SECRET_KEY、构建并启动
# 后续更新：
bash deploy/update.sh     # git pull + 重建 + 滚动重启（数据保留在 data/ 卷）
```

详见 [docs/DEPLOY.md](docs/DEPLOY.md)。

---

## 配置说明（`.env`）

| 变量 | 说明 | 默认 |
|------|------|------|
| `SECRET_KEY` | JWT 签名 + Key 加密的根密钥，**生产必改长随机串** | — |
| `DATABASE_URL` | 留空=SQLite；切 PG/MySQL 填连接串 | SQLite |
| `DEFAULT_ADMIN_USERNAME/PASSWORD` | 首次启动播种的管理员 | `Admin` / `Seek22626301` |
| `PROVIDER_MOCK` | `true`=Mock 数据源（无 Key/离线调试）；服务器置 `false` | `false` |
| `DAJIALA_BASE_URL` | dajiala API 地址 | `https://www.dajiala.com` |
| `CORS_ORIGINS` | 前端来源（Docker 下同源反代，无需配置） | dev 端口 |
| `FETCH_CONCURRENCY` / `ANALYSIS_CONCURRENCY` | 抓取/分析并发 | 3 / 3 |

所有第三方 Key（dajiala / LLM / MCP / LightPanda / Tavily）均在**前端「设置」页配置**，Fernet 加密落库，不写死在代码里。

---

## 使用流程（验收路径）

1. 登录 `Admin / Seek22626301` → 改密。
2. **设置 → 数据源 Key**：填一个 dajiala Key（离线调试可跳过，用 Mock）。
3. **公众号管理**：批量导入或检索添加几个测试公众号。
4. **内容抓取**：选账号+时间段+勾选字段 → 发起 → 看任务进度。
5. **文章库**：查看/过滤/排序/多选 → 一键导出 Excel。
6. **设置 → 大模型**：配一个 OpenAI 兼容模型。
7. **智能分析**：建模块+维度 → 单篇/批量运行 → 查看/导出结果。
8. **定时任务**：建 cron 任务 → 运行 → 看阅读排名报告。
9. **待确认**：重抓遇到删除/评论下降 → 队列处理（保留/删除）。

---

## 待办 / 已知边界

- **dajiala 字段级映射**：✅ 已于 2026-08 按官方 Apifox 文档对齐（见 `docs/dajiala_api/` 存档）。要点：全部接口 **POST+JSON**；历史发文 offset 翻页、评论 buffer 翻页、搜索 page/size；post_history 用 ghid 不用 biz。`backend/app/providers/dajiala.py` 顶部集中了 `ENDPOINTS` 与各 `*_FIELD_MAP` / 错误码，官方若调整只改这些常量。
- **出站代理**：本机/内网需在 `.env` 配 `HTTP_PROXY` + `HTTP_VERIFY_SSL=false`（华为代理做 SSL MITM）；云服务器直连留空即可。
- **外部连通性**：dajiala（Key 校验走免费 `get_remain_money`）、Tavily、LightPanda 已实测连通；MCP 视具体 server。
- 视频号 / 全网热词检索为 M3，经 `SourceProvider` 接口扩展。

## 测试

```bash
cd backend
pytest            # 使用 Mock 数据源与 Mock LLM，无需外网
```
