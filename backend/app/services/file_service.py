from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.schemas import GeneratedFile


class FileService:
    def __init__(self, generated_dir: Path | None = None) -> None:
        self.generated_dir = generated_dir or get_settings().generated_path

    def list_files(self) -> list[GeneratedFile]:
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        files: list[GeneratedFile] = []
        for path in sorted(self.generated_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
            files.append(self._to_generated_file(path))
        return files

    def get_file_path(self, file_id: str) -> Path | None:
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        matches = list(self.generated_dir.glob(f"{file_id}*.md"))
        return matches[0] if matches else None

    def write_markdown(self, title: str, body: str, name_hint: str | None = None) -> GeneratedFile:
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        source = name_hint or title
        safe_title = "".join(char for char in source if char.isalnum() or char in ("-", "_"))[:36] or "study-note"
        file_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
        path = self.generated_dir / f"{file_id}-{safe_title}.md"
        path.write_text(body, encoding="utf-8")
        return self._to_generated_file(path)

    def _to_generated_file(self, path: Path) -> GeneratedFile:
        stat = path.stat()
        return GeneratedFile(
            id=path.stem,
            name=path.name,
            path=str(path),
            created_at=datetime.fromtimestamp(stat.st_mtime),
        )
