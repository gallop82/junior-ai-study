# Backend

FastAPI + LangGraph 后端。

## 启动

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

未配置 `OPENAI_API_KEY` 时，会使用本地 fallback 回答，方便先联调。

## SQLite

默认数据库路径：

```text
backend/data/app.db
```

启动时会自动创建 `wechat_articles` 表。公众号接入后，把文章写入这个表即可被 `/api/chat` 检索。

## API

```text
GET  /api/health
GET  /api/skills
GET  /api/teachers
POST /api/chat
GET  /api/generated-files
GET  /api/generated-files/{file_id}
```

