from pathlib import Path

from app.config import get_settings
from app.schemas import Skill, SkillSummary
from app.utils.frontmatter import parse_frontmatter


class SkillService:
    def __init__(self, skills_dir: Path | None = None) -> None:
        self.skills_dir = skills_dir or get_settings().skills_dir

    def list_skills(self) -> list[SkillSummary]:
        return [
            SkillSummary(**self._load_skill(path).model_dump(exclude={"content"}))
            for path in self._skill_paths()
        ]

    def get(self, skill_id: str) -> Skill | None:
        for path in self._skill_paths():
            skill = self._load_skill(path)
            if skill.id == skill_id:
                return skill
        return None

    def get_many(self, skill_ids: list[str]) -> list[Skill]:
        by_id = {skill.id: skill for skill in (self._load_skill(path) for path in self._skill_paths())}
        return [by_id[skill_id] for skill_id in skill_ids if skill_id in by_id]

    def _skill_paths(self) -> list[Path]:
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        single_file_skills = sorted(self.skills_dir.glob("*.md"))
        directory_skills = sorted(path / "SKILL.md" for path in self.skills_dir.iterdir() if (path / "SKILL.md").is_file())
        return single_file_skills + directory_skills

    def _load_skill(self, path: Path) -> Skill:
        raw = path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(raw)
        fallback_id = path.parent.name if path.name == "SKILL.md" else path.stem
        return Skill(
            id=metadata.get("id") or metadata.get("name") or fallback_id,
            name=metadata.get("name") or fallback_id,
            subject=metadata.get("subject") or None,
            description=metadata.get("description") or "",
            content=body or raw,
        )
