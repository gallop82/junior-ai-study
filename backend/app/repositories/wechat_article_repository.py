import sqlite3
from pathlib import Path

from app.config import get_settings
from app.schemas import WechatArticle


class WechatArticleRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or get_settings().sqlite_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    def ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS wechat_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT,
                    title TEXT NOT NULL,
                    url TEXT,
                    summary TEXT,
                    content TEXT,
                    subject TEXT,
                    grade TEXT,
                    tags TEXT,
                    published_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_wechat_articles_account ON wechat_articles(account_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_wechat_articles_title ON wechat_articles(title)")

    def search(self, question: str, account_id: str | None = None, limit: int = 5) -> list[WechatArticle]:
        if not question.strip():
            return []

        keywords = self._keywords(question)
        if not keywords:
            return []

        where_parts: list[str] = []
        params: list[str | int] = []
        if account_id:
            where_parts.append("account_id = ?")
            params.append(account_id)

        keyword_parts = []
        for keyword in keywords:
            keyword_parts.append("(title LIKE ? OR summary LIKE ? OR content LIKE ? OR tags LIKE ?)")
            like = f"%{keyword}%"
            params.extend([like, like, like, like])

        where_parts.append("(" + " OR ".join(keyword_parts) + ")")
        params.append(limit)

        sql = f"""
            SELECT id, account_id, title, url, summary, content, published_at
            FROM wechat_articles
            WHERE {' AND '.join(where_parts)}
            ORDER BY published_at DESC, id DESC
            LIMIT ?
        """

        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [WechatArticle(**dict(row)) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _keywords(self, question: str) -> list[str]:
        clean = question.strip()
        tokens = [token for token in clean.replace("，", " ").replace("。", " ").replace("？", " ").replace("?", " ").split() if token]
        if tokens:
            return tokens[:6]
        return [clean[:20]]

