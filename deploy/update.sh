#!/usr/bin/env bash
# 一键更新（在云服务器项目根目录执行：bash deploy/update.sh）
# 流程：拉代码 → 重建镜像 → 重启容器（数据在 ../data 卷中，重建不丢）
set -euo pipefail

cd "$(dirname "$0")/.."   # 项目根

echo "==> 拉取最新代码 ..."
if git rev-parse --git-dir >/dev/null 2>&1; then
  git pull --rebase
else
  echo "    当前目录不是 git 仓库，跳过 git pull（请手动更新代码）"
fi

echo "==> 重建并滚动重启 ..."
docker compose -f deploy/docker-compose.yml up -d --build

echo "==> 清理悬空镜像 ..."
docker image prune -f >/dev/null 2>&1 || true

echo "==> 更新完成！"
docker compose -f deploy/docker-compose.yml ps
