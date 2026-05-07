from app.repositories.wechat_article_repository import WechatArticleRepository
from app.schemas import Teacher, WechatArticle


class ArticleRetriever:
    def __init__(self, repository: WechatArticleRepository | None = None) -> None:
        self.repository = repository or WechatArticleRepository()

    def retrieve(self, question: str, teacher: Teacher, limit: int = 5) -> list[WechatArticle]:
        return self.repository.search(question=question, account_id=teacher.wechat_account_id, limit=limit)

