from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import ChatMessage, Skill, Teacher, WechatArticle


class LlmService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def stream_answer(
        self,
        question: str,
        teacher: Teacher,
        skills: list[Skill],
        articles: list[WechatArticle],
        history: list[ChatMessage],
    ) -> AsyncIterator[str]:
        if not self.settings.openai_api_key:
            for char in self._fallback_answer(question, teacher, skills, articles):
                yield char
            return

        client = AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
        )
        stream = await client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": self._system_prompt(teacher, skills, articles)},
                {"role": "user", "content": self._human_prompt(question, history)},
            ],
            temperature=0.4,
            stream=True,
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    def _system_prompt(self, teacher: Teacher, skills: list[Skill], articles: list[WechatArticle]) -> str:
        skill_text = "\n\n".join(f"## {skill.name}\n{skill.content}" for skill in skills) or "未选择 skill。"
        article_text = "\n\n".join(
            f"标题：{article.title}\n摘要：{article.summary or ''}\n内容片段：{(article.content or '')[:800]}"
            for article in articles
        ) or "微信公众号内容暂未接入或未检索到相关材料。"

        return (
            f"你是{teacher.name}，一位面向初中生的 AI 问答老师。\n"
            f"老师说明：{teacher.description or '公众号内容待接入，当前使用通用问答能力。'}\n"
            "回答要清楚、具体、适合初中生理解。可以使用 Markdown 标题、列表和表格组织内容。"
            "不要声称自己是真人本人。\n\n"
            f"可用 skills：\n{skill_text}\n\n"
            f"微信公众号文章材料：\n{article_text}"
        )

    def _human_prompt(self, question: str, history: list[ChatMessage]) -> str:
        history_text = "\n".join(f"{message.role}: {message.content}" for message in history[-8:])
        return f"历史对话：\n{history_text}\n\n学生问题：{question}"

    def _fallback_answer(
        self,
        question: str,
        teacher: Teacher,
        skills: list[Skill],
        articles: list[WechatArticle],
    ) -> str:
        skill_names = "、".join(skill.name for skill in skills) or "通用问答"
        article_note = (
            f"我参考了 {len(articles)} 条已接入的微信文章材料。"
            if articles
            else "公众号内容还没有接入或没有检索到相关材料，我先用通用学习方法回答。"
        )
        return (
            f"{teacher.name}：{article_note}\n\n"
            f"## 当前技能\n\n{skill_names}\n\n"
            f"## 问题\n\n{question}\n\n"
            "## 建议\n\n"
            "- 先把问题拆成“已知信息、不会的点、希望得到的结果”三部分。\n"
            "- 如果是题目，把原题和你的解题过程发出来。\n"
            "- 如果是复习目标，告诉我科目、章节和当前薄弱点。"
        )
