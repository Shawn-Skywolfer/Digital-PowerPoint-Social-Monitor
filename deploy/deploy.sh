#!/usr/bin/env bash
# 一键部署（在云服务器项目根目录执行：bash deploy/deploy.sh）
set -euo pipefail

cd "$(dirname "$0")/.."   # 切到项目根

echo "==> 检查 Docker / docker compose ..."
command -v docker >/dev/null 2>&1 || { echo "未安装 docker，请先安装"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "未安装 docker compose 插件"; exit 1; }

# 1. 准备 .env
if [ ! -f .env ]; then
  echo "==> 未发现 .env，复制 .env.example 生成 ..."
  cp .env.example .env
fi

# 2. 生产必须改 SECRET_KEY（JWT 签名 + Key 加密都依赖它）
if grep -q "^SECRET_KEY=please-change-me" .env || grep -q "^SECRET_KEY=$" .env; then
  NEWKEY="$(head -c 48 /dev/urandom | od -An -tx1 | tr -d ' \n')"
  if grep -q "^SECRET_KEY=" .env; then
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=${NEWKEY}/" .env
  else
    echo "SECRET_KEY=${NEWKEY}" >> .env
  fi
  echo "==> 已自动生成长随机 SECRET_KEY 写入 .env"
fi

# 3. 生产关闭 Mock 数据源（用真实 dajiala）；本地调试可手动改回 true
if grep -q "^PROVIDER_MOCK=true" .env; then
  sed -i "s/^PROVIDER_MOCK=true/PROVIDER_MOCK=false/" .env
  echo "==> 已将 PROVIDER_MOCK 置为 false（使用真实 dajiala 数据源）"
fi

mkdir -p data/exports

echo "==> 构建并启动容器 ..."
docker compose -f deploy/docker-compose.yml up -d --build

echo ""
echo "==> 部署完成！"
echo "    前端入口: http://<服务器IP>/   （compose 默认映射 80 端口）"
echo "    默认账号: Admin / Seek22626301 （首次登录请改密）"
echo "    查看日志: docker compose -f deploy/docker-compose.yml logs -f"
echo ""
echo "    提示：服务器需能访问外网（dajiala API、大模型、MCP/LightPanda/Tavily 端点）。"
