# 后端镜像：FastAPI + uvicorn
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 系统依赖（httpx/openssl 已含；保留 curl 便于健康检查）
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖（利用层缓存）
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install -r /app/backend/requirements.txt

# 拷贝代码：保持 backend/app/... 结构，使 BASE_DIR(=parents[3]) 解析为 /app
COPY backend/ /app/backend/

# 数据目录（sqlite + exports），由卷挂载持久化
RUN mkdir -p /app/data/exports

WORKDIR /app/backend
ENV PYTHONPATH=/app/backend

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
