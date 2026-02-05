# ========== 阶段 1：前端构建（仅在构建期使用 Node） ==========
FROM node:20-alpine AS frontend-build

# 设置前端工作目录
WORKDIR /app/frontend

# 仅复制包清单以最大化缓存命中；若存在 lockfile，推荐改用 `npm ci`
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

# 复制前端源码并构建静态产物，输出到 /app/frontend/dist
COPY frontend/ ./
RUN npx vite build

# ========== 阶段 2：后端运行镜像（仅保留 Python 运行环境） ==========
FROM python:3.12-slim AS runtime

# 设置工作目录
WORKDIR /app

# 安装健康检查所需工具，创建非 root 用户，并准备数据目录
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app/data

# 先复制依赖清单并安装，利用 pip 缓存层
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源码
COPY backend/ .

# 复制前端构建产物至后端静态目录，FastAPI 将挂载并提供前端页面
COPY --from=frontend-build /app/frontend/dist ./static

# 目录所有权调整并切换到非 root 用户，提升安全性
RUN chown -R appuser:appuser /app
USER appuser

# 暴露服务端口：后端 API 与前端静态同端口提供
EXPOSE 8000

# 运行时配置（可由 docker-compose 或部署平台覆盖）
ENV UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000 \
    UVICORN_WORKERS=2

# 健康检查：访问自动生成的文档页，若失败则判定不健康
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${UVICORN_PORT}/docs || exit 1

# 同时提供后端 API 与前端静态站点（挂载在根路径 /）
CMD ["sh", "-c", "uvicorn app.main:app --host ${UVICORN_HOST} --port ${UVICORN_PORT} --workers ${UVICORN_WORKERS}"]
