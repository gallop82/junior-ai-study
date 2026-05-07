from datetime import datetime

from pydantic import BaseModel, Field


class SkillSummary(BaseModel):
    id: str
    name: str
    subject: str | None = None
    description: str = ""


class Skill(SkillSummary):
    content: str


class Teacher(BaseModel):
    id: str
    name: str
    description: str = ""
    wechat_account_id: str | None = None
    is_connected: bool = False


class WechatArticle(BaseModel):
    id: int
    account_id: str | None = None
    title: str
    url: str | None = None
    summary: str | None = None
    content: str | None = None
    published_at: str | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    teacher_id: str
    skill_ids: list[str] = Field(default_factory=list)
    history: list[ChatMessage] = Field(default_factory=list)
    generate_file: bool = True


class GeneratedFile(BaseModel):
    id: str
    name: str
    path: str
    created_at: datetime


class ChatResponse(BaseModel):
    answer: str
    teacher: Teacher
    used_skills: list[SkillSummary]
    articles: list[WechatArticle] = Field(default_factory=list)
    files: list[GeneratedFile] = Field(default_factory=list)


class TtsRequest(BaseModel):
    text: str = Field(..., max_length=5000)
