# 部署手册

## 架构

```
浏览器 ──80──> [frontend 容器] nginx ──/api──> [backend 容器] FastAPI:8000
                    │ 静态产物(dist)                  │ SQLAlchemy
                    └─ /health 反代 ───────────────> │ SQLite(WAL)/PG/MySQL
                                                       └─ /app/data (卷持久化)
```

- **frontend**：构建 Vue3 产物并用 nginx 托管，反代 `/api`、`/health` 到后端。
- **backend**：uvicorn 跑 FastAPI；定时任务（APScheduler）随进程内运行。
- **数据**：`../data`（项目根的 `data/`）挂载到容器 `/app/data`，含 `monitor.db` 与 `exports/`，**容器重建不丢数据**。

## 前置条件

1. 云服务器已装 **docker** 与 **docker compose 插件**。
2. 服务器**能访问外网**（dajiala API、大模型端点、MCP/LightPanda/Tavily 端点）。如在内网需开放相应出站策略。
3. 代码已在服务器上（git clone 或上传）。

## 首次部署

```bash
bash deploy/deploy.sh
```

脚本会：
- 校验 docker / compose 可用；
- 若无 `.env` 则从 `.env.example` 复制；
- 自动生成**长随机 `SECRET_KEY`** 写入 `.env`（JWT 签名 + Key 加密依赖它）；
- 把 `PROVIDER_MOCK` 置为 `false`（生产用真实 dajiala）；
- `docker compose -f deploy/docker-compose.yml up -d --build`。

部署后访问 `http://<服务器IP>/`（默认 80 端口）。改端口：编辑 `deploy/docker-compose.yml` 里 frontend 的 `ports`。

## 更新

```bash
bash deploy/update.sh     # git pull + 重建 + 滚动重启
```

## 常用运维命令

```bash
# 查看状态 / 日志
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml logs -f backend
docker compose -f deploy/docker-compose.yml logs -f frontend

# 重启 / 停止
docker compose -f deploy/docker-compose.yml restart
docker compose -f deploy/docker-compose.yml down          # 停并删容器（数据卷仍在）

# 备份数据（sqlite + 导出文件）
tar czf backup_$(date +%F).tgz data/
```

## 切换数据库（可选）

默认 SQLite（WAL）。多人并发或数据量大时切 PostgreSQL：

```yaml
# deploy/docker-compose.yml 增加：
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: monitor
      POSTGRES_PASSWORD: <强密码>
      POSTGRES_DB: monitor
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks: [appnet]
volumes:
  pgdata:
```

并在 `.env` 设置：

```
DATABASE_URL=postgresql+psycopg://monitor:<强密码>@postgres:5432/monitor
```

（需在 `backend/requirements.txt` 增加 `psycopg[binary]`。）

## 环境变量

见根目录 `README.md` 的「配置说明」。生产关键项：

- `SECRET_KEY`：必须长随机（脚本已自动生成）。
- `PROVIDER_MOCK=false`：生产用真实 dajiala。
- `CORS_ORIGINS`：Docker 下同源反代，无需配置；若前后端分离部署，填前端域名。

## 安全清单

- [ ] `.env` 的 `SECRET_KEY` 为长随机串（勿入库、勿外泄）。
- [ ] 首登后立即修改 `Admin` 默认密码。
- [ ] 云安全组仅放行必要端口（默认 80）。
- [ ] 定期备份 `data/`。
- [ ] 所有第三方 Key 在前端设置页配置（加密落库），勿写进代码/镜像。
