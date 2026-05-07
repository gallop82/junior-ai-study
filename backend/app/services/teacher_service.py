import json
from pathlib import Path

from app.config import get_settings
from app.schemas import Teacher
from app.utils.frontmatter import parse_frontmatter


class TeacherService:
    def __init__(self, teachers_dir: Path | None = None) -> None:
        self.teachers_dir = teachers_dir or get_settings().teachers_dir

    def list_teachers(self) -> list[Teacher]:
        self.teachers_dir.mkdir(parents=True, exist_ok=True)
        teachers = [self._load_teacher(path) for path in sorted(self.teachers_dir.glob("*")) if path.suffix in {".json", ".yaml", ".yml"}]
        return teachers

    def get(self, teacher_id: str) -> Teacher:
        teachers = self.list_teachers()
        for teacher in teachers:
            if teacher.id == teacher_id:
                return teacher
        if teachers:
            return teachers[0]
        return Teacher(id="default", name="默认老师", description="公众号内容待接入，当前使用通用问答能力。")

    def _load_teacher(self, path: Path) -> Teacher:
        raw = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            payload = json.loads(raw)
        else:
            payload, _ = parse_frontmatter(f"---\n{raw}\n---")
        return Teacher(
            id=payload.get("id") or path.stem,
            name=payload.get("name") or path.stem,
            description=payload.get("description") or "",
            wechat_account_id=payload.get("wechat_account_id") or None,
            is_connected=bool(payload.get("wechat_account_id")),
        )

