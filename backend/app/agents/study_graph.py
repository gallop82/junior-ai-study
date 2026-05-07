from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas import ChatMessage, GeneratedFile, Skill, Teacher, WechatArticle
from app.services.article_retriever import ArticleRetriever
from app.services.file_service import FileService
from app.services.llm_service import LlmService
from app.services.skill_service import SkillService
from app.services.teacher_service import TeacherService


class StudyState(TypedDict):
    question: str
    teacher_id: str
    skill_ids: list[str]
    history: list[ChatMessage]
    generate_file: bool
    teacher: Teacher | None
    skills: list[Skill]
    articles: list[WechatArticle]
    answer: str
    files: list[GeneratedFile]


class StudyGraph:
    def __init__(
        self,
        teacher_service: TeacherService | None = None,
        skill_service: SkillService | None = None,
        article_retriever: ArticleRetriever | None = None,
        llm_service: LlmService | None = None,
        file_service: FileService | None = None,
    ) -> None:
        self.teacher_service = teacher_service or TeacherService()
        self.skill_service = skill_service or SkillService()
        self.article_retriever = article_retriever or ArticleRetriever()
        self.llm_service = llm_service or LlmService()
        self.file_service = file_service or FileService()
        self.graph = self._build_graph()

    def invoke(
        self,
        question: str,
        teacher_id: str,
        skill_ids: list[str],
        history: list[ChatMessage],
        generate_file: bool,
    ) -> StudyState:
        return self.graph.invoke(
            {
                "question": question,
                "teacher_id": teacher_id,
                "skill_ids": skill_ids,
                "history": history,
                "generate_file": generate_file,
                "teacher": None,
                "skills": [],
                "articles": [],
                "answer": "",
                "files": [],
            }
        )

    def _build_graph(self):
        graph = StateGraph(StudyState)
        graph.add_node("load_teacher", self._load_teacher)
        graph.add_node("load_skills", self._load_skills)
        graph.add_node("retrieve_articles", self._retrieve_articles)
        graph.add_node("generate_answer", self._answer)
        graph.add_node("write_file_if_needed", self._maybe_generate_file)

        graph.add_edge(START, "load_teacher")
        graph.add_edge("load_teacher", "load_skills")
        graph.add_edge("load_skills", "retrieve_articles")
        graph.add_edge("retrieve_articles", "generate_answer")
        graph.add_edge("generate_answer", "write_file_if_needed")
        graph.add_edge("write_file_if_needed", END)
        return graph.compile()

    def _load_teacher(self, state: StudyState) -> StudyState:
        state["teacher"] = self.teacher_service.get(state["teacher_id"])
        return state

    def _load_skills(self, state: StudyState) -> StudyState:
        state["skills"] = self.skill_service.get_many(state["skill_ids"])
        return state

    def _retrieve_articles(self, state: StudyState) -> StudyState:
        teacher = state["teacher"]
        state["articles"] = self.article_retriever.retrieve(state["question"], teacher) if teacher else []
        return state

    def _answer(self, state: StudyState) -> StudyState:
        teacher = state["teacher"] or Teacher(
            id="default",
            name="默认老师",
            description="公众号内容待接入，当前使用通用问答能力。",
        )
        state["teacher"] = teacher
        state["answer"] = self.llm_service.answer(
            question=state["question"],
            teacher=teacher,
            skills=state["skills"],
            articles=state["articles"],
            history=state["history"],
        )
        return state

    def _maybe_generate_file(self, state: StudyState) -> StudyState:
        if not state["generate_file"]:
            return state
        title = state["question"][:24]
        name_hint = state["skills"][0].name if state["skills"] else title
        article_refs = "\n".join(f"- {article.title} {article.url or ''}" for article in state["articles"])
        body = f"# {title}\n\n{state['answer']}\n"
        if article_refs:
            body += f"\n## 引用材料\n\n{article_refs}\n"
        state["files"] = [self.file_service.write_markdown(title, body, name_hint=name_hint)]
        return state

