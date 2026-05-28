# Dokploy 部署指南

本项目已完成 Docker 化配置，可以直接在安装了 Dokploy 的 Ubuntu 服务器上进行部署。

## 部署步骤

### 1. 准备工作
- 确保服务器已安装 Docker 和 Dokploy。
- 获取 Siliconflow 的 API KEY。

### 2. 在 Dokploy 中创建项目
1. 在 Dokploy 面板中，创建一个新的 **Project**。
2. 在项目内创建一个 **Compose** 服务。

### 3. 配置环境变量
在 Compose 服务的 **Environment** 选项卡中，参考 `.env.example` 添加以下变量：
- `OPENAI_API_KEY`: 你的 Siliconflow API Key。
- `OPENAI_BASE_URL`: `https://api.siliconflow.cn/v1`。

### 4. 部署 Compose
1. 将项目根目录下的 `docker-compose.yml` 内容复制并粘贴到 Dokploy 的 Compose 编辑器中。
2. 点击 **Deploy**。

### 5. 访问应用
- 默认配置下，前端服务运行在 `3000` 端口。
- 你可以在 Dokploy 中为 `frontend` 服务配置域名。
- API 服务已通过 Nginx 反向代理（`/api`），无需额外暴露 API 端口。

## 服务说明
- **db**: PostgreSQL 15 数据库，数据持久化在 `pgdata` 卷中。
- **api**: FastAPI 后端，负责提供数据接口。
- **scheduler**: 爬虫调度器，每天早上 8:00 自动执行抓取任务。
- **frontend**: React/Vite 前端，使用 Nginx 进行生产级托管。

## 注意事项
- 首次部署时，`api` 服务会自动创建数据库表。
- 爬虫任务会在 `scheduler` 容器启动时立即运行一次，随后进入定时循环。
- 如果需要手动触发爬虫，可以进入 `scheduler` 容器执行 `python run_scraper.py`。
