# Junior AI Study

一个基于 FastAPI + LangGraph 的学习助手项目，前后端分离。

## 目录结构

- `backend/`：FastAPI 后端
- `frontend/`：Vue 3 + Vite 前端

## Linux 环境要求

- Python 3.10+
- Node.js 18+
- `npm`
- `pm2`（可选，但推荐用于后台托管）

## 后端配置

后端通过 `backend/.env` 读取环境变量。常用配置如下：

```env
APP_NAME=Junior AI Study
OPENAI_API_KEY=你的密钥
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
SQLITE_DB_PATH=data/app.db
GENERATED_DIR=generated
```

说明：

- `OPENAI_API_KEY` 不配置时，项目会走本地 fallback 回复
- SQLite 默认数据库路径是 `backend/data/app.db`
- 运行时会自动创建所需表结构

## 本地启动

### 1. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可以访问：

- `GET http://127.0.0.1:8000/api/health`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

Vite 默认会启动在 `http://127.0.0.1:5173`。

前端开发环境下会把 `/api` 代理到后端 `http://127.0.0.1:8000`。

## PM2 启动

### 1. 安装 PM2

```bash
npm i -g pm2
```

### 2. 启动后端

先确保后端虚拟环境已经创建并安装过依赖：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

然后用 PM2 托管：

```bash
cd /path/to/junior-ai-study
pm2 start backend/.venv/bin/python --name junior-backend --cwd backend --interpreter none -- -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. 启动前端

#### 开发模式

```bash
cd /path/to/junior-ai-study
pm2 start npm --name junior-frontend --cwd frontend -- run dev
```

#### 生产模式

先构建前端：

```bash
cd frontend
npm install
npm run build
```

然后用 PM2 提供静态文件服务：

```bash
cd /path/to/junior-ai-study
pm2 serve frontend/dist 5173 --spa --name junior-frontend
```

> 生产环境更推荐使用 Nginx 直接托管 `frontend/dist`，再把 `/api` 反向代理到后端 `8000` 端口。

## PM2 常用命令

```bash
pm2 status
pm2 logs junior-backend
pm2 logs junior-frontend
pm2 restart junior-backend
pm2 restart junior-frontend
pm2 stop junior-backend
pm2 stop junior-frontend
pm2 save
pm2 startup
```

## 前端自动转发到后端

如果你希望“前端页面访问后自动把 `/api` 转发到后端 8000”，生产环境不要只用 `pm2 serve`，而是要加一层反向代理，比如 Nginx。

### 推荐方式

1. 前端代码里请求相对路径 `/api`，当前项目已经这样处理了。
2. 后端继续监听 `127.0.0.1:8000` 或 `0.0.0.0:8000`。
3. Nginx 对外提供 `80/443`，把 `/api` 转发到 `8000`，把前端静态文件直接返回。

### 示例 Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/junior-ai-study/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 这样访问时的链路

- 浏览器访问 `http://your-domain.com`
- 前端静态文件由 Nginx 返回
- 前端里的 `/api/...` 由 Nginx 转发到 `http://127.0.0.1:8000/api/...`

## 常见访问地址

- 前端开发模式：`http://127.0.0.1:5173`
- 后端接口：`http://127.0.0.1:8000`

## 说明

- 如果你使用域名和 HTTPS，建议让 Nginx 统一对外提供 80/443 服务
- 如果前后端不在同一台机器，需要手动调整前端的 API 地址配置
