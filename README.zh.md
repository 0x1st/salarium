# Salarium — 薪资管理

![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=githubactions) ![License](https://img.shields.io/badge/License-Private-lightgrey) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi) ![Vue 3](https://img.shields.io/badge/Vue_3-4FC08D?logo=vuedotjs) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)

Salarium 是一个轻量的演示应用，结合 FastAPI 后端与 Vue 3 + Vite 前端，面向家庭或私有化的薪资管理场景，注重简单易用与良好的开发体验。

## ✨ 亮点
- 🏠 家庭/私有薪资：适用于家庭或小型自托管场景。
- 🔐 认证就绪：本地环境的注册/登录流程友好。
- 💸 薪资记录：轻松新增、编辑与整理薪酬数据。
- 📊 快速概览：简单汇总以了解月度总额等信息。
- 🧱 SQLite 优先：便携、零配置的本地数据库。

## 🧩 技术栈
- FastAPI + Uvicorn：高性能、类型安全的后端 API。
- Tortoise ORM + SQLite：简单直观的持久化方案。
- Vue 3 + Vite：前端开发高效，支持 HMR 热更新。
- 模块化后端路由：清晰的代码结构与易维护性。

## 📁 目录结构
```
backend/          # FastAPI 应用（routes、models、schemas、services、utils）
frontend/         # Vue 3 + Vite 前端项目
README.en.md      # 英文文档
README.zh.md      # 中文文档
```

## 🚀 快速开始

### 方式一：DockerHub 拉取运行（推荐）

#### 前置条件
- Docker 和 Docker Compose

#### 启动步骤
```bash
# 直接拉取镜像并运行（容器内部端口 8000，需要映射到主机）
docker pull styin8/salarium:latest
docker run -d \
  --name salarium \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  styin8/salarium:latest

# 访问应用
# 前端：http://localhost:8000
# API 文档：http://localhost:8000/docs
# API：http://localhost:8000/api
```

**特性**：
- ✅ 单容器部署，FastAPI 同时托管前端静态资源和 API
- ✅ 自动健康检查
- ✅ SQLite 数据持久化到 `./data/` 目录
- ✅ 支持 SPA 路由回退

详细部署文档请参考 [DEPLOY.md](DEPLOY.md)。

### 方式二：Docker 单容器（本地构建）
```bash
docker compose up -d --build
# 前端/API 入口：http://localhost:8000
```

### 方式二：本地开发

#### 前置条件
- Python 3.12（推荐）
- Node.js >= 18

#### 后端启动
推荐（uv）：
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

备选（virtualenv）：
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

首次运行会初始化 Tortoise ORM 并创建 SQLite 数据库。

#### 前端启动
```bash
cd frontend
npm install
npm run dev
```

打开开发服务器（通常为 `http://localhost:5173`），前端会通过代理访问后端 API。

## 🖼 截图
- 仪表盘（占位）：`docs/images/dashboard.png`
- 薪资页面（占位）：`docs/images/salaries.png`

## 🏗 架构
```
[Vue 3 + Vite] → Axios → [FastAPI] → Tortoise ORM → [SQLite]
```

## 🛠 开发说明
- 🧹 `.gitignore` 已忽略 SQLite 产物（`*.db`、`*.db-wal`、`*.db-shm`）。
- 🔐 机密信息请使用环境变量管理，避免提交凭据。
- 🔄 后端建议在 `127.0.0.1:8000` 运行，便于前端对接。