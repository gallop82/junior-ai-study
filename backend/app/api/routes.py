import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.schemas import ChatRequest, GeneratedFile, Skill, SkillSummary, Teacher, TtsRequest
from app.services.article_retriever import ArticleRetriever
from app.services.file_service import FileService
from app.services.llm_service import LlmService
from app.services.skill_service import SkillService
from app.services.teacher_service import TeacherService
from app.services.tts_service import TtsService

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/skills", response_model=list[SkillSummary])
def list_skills() -> list[SkillSummary]:
    return SkillService().list_skills()


@router.get("/skills/{skill_id}", response_model=Skill)
def get_skill(skill_id: str) -> Skill:
    skill = SkillService().get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found.")
    return skill


@router.get("/teachers", response_model=list[Teacher])
def list_teachers() -> list[Teacher]:
    return TeacherService().list_teachers()


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest):
    async def event_stream():

        yield _sse_data({"content": "", "done": False, "ready": True})

        teacher_service = TeacherService()
        skill_service = SkillService()
        article_retriever = ArticleRetriever()
        llm_service = LlmService()
        file_service = FileService()

        teacher = teacher_service.get(payload.teacher_id)
        skills = skill_service.get_many(payload.skill_ids)
        articles = article_retriever.retrieve(payload.question, teacher)

        answer_parts: list[str] = []
        async for chunk in llm_service.stream_answer(
            question=payload.question,
            teacher=teacher,
            skills=skills,
            articles=articles,
            history=payload.history,
        ):
            answer_parts.append(chunk)
            yield _sse_data({"content": chunk, "done": False})

        answer = "".join(answer_parts)
        files = []
        if payload.generate_file:
            title = payload.question[:24]
            name_hint = skills[0].name if skills else title
            article_refs = "\n".join(
                f"- {article.title} {article.url or ''}" for article in articles
            )
            body = f"# {title}\n\n{answer}\n"
            if article_refs:
                body += f"\n## 引用材料\n\n{article_refs}\n"
            files = [file_service.write_markdown(title, body, name_hint=name_hint)]

        yield _sse_data(
            {
                "content": "",
                "done": True,
                "answer": answer,
                "teacher": teacher.model_dump(),
                "used_skills": [
                    skill.model_dump(exclude={"content"}) for skill in skills
                ],
                "articles": [article.model_dump() for article in articles],
                "files": [file.model_dump(mode="json") for file in files],
            }
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse_data(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"


@router.get("/generated-files", response_model=list[GeneratedFile])
def list_generated_files() -> list[GeneratedFile]:
    return FileService().list_files()


@router.get("/generated-files/{file_id}")
def get_generated_file(file_id: str):
    path = FileService().get_file_path(file_id)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        path, media_type="text/markdown; charset=utf-8", filename=path.name
    )


@router.post("/tts")
async def text_to_speech(payload: TtsRequest):
    tts = TtsService()
    try:
        audio_path = await tts.generate(payload.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return FileResponse(audio_path, media_type="audio/mpeg", filename="speech.mp3")
