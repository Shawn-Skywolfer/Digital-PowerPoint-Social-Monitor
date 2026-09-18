# 前端镜像：构建 Vue3 静态产物 → nginx 托管 + 反向代理后端
# ---- 构建阶段 ----
FROM node:20-slim AS build
WORKDIR /build

# 使用 npmmirror 加速（可在服务器上按需删除）
RUN npm config set registry https://registry.npmmirror.com

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# ---- 运行阶段 ----
FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /build/dist /usr/share/nginx/html

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
