import hashlib
import re
from pathlib import Path

import edge_tts

from app.config import get_settings


class TtsService:
    VOICE = "zh-CN-XiaoxiaoNeural"
    MAX_CHUNK = 2000

    def __init__(self, cache_dir: Path | None = None) -> None:
        settings = get_settings()
        self.cache_dir = cache_dir or (settings.generated_path / "tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ── markdown cleaning ────────────────────────────────────────────

    @staticmethod
    def clean_markdown(text: str) -> str:
        """Strip Markdown formatting so TTS reads natural sentences."""
        # code blocks
        text = re.sub(r"```[\s\S]*?```", "", text)
        # remove inline code backticks
        text = text.replace("`", "")
        # remove bold/italic stars (this is the most common issue!)
        text = text.replace("*", "")
        # remove headers hashes
        text = re.sub(r"#{1,6}\s*", "", text)
        # links → keep text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # images → remove completely
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        # HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        # blockquotes
        text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)
        # list markers
        text = re.sub(r"^\s*[-+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)
        # tables / horizontal rules
        text = re.sub(r"\|", " ", text)
        text = re.sub(r"^[-_]{3,}\s*$", "", text, flags=re.MULTILINE)
        # collapse blank lines
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip()

    # ── text splitting ───────────────────────────────────────────────

    def _split_text(self, text: str) -> list[str]:
        if len(text) <= self.MAX_CHUNK:
            return [text]
        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) + 2 > self.MAX_CHUNK and current:
                chunks.append(current.strip())
                current = para
            else:
                current = f"{current}\n\n{para}" if current else para
        if current.strip():
            chunks.append(current.strip())
        return chunks or [text]

    # ── cache ────────────────────────────────────────────────────────

    @staticmethod
    def _text_hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    # ── generate ─────────────────────────────────────────────────────

    async def generate(self, text: str) -> Path:
        """Return path to an mp3 file for the given text (cached)."""
        clean = self.clean_markdown(text)
        if not clean:
            raise ValueError("清洗后文本为空，无法生成语音。")

        cache_key = self._text_hash(clean)
        cache_path = self.cache_dir / f"{cache_key}.mp3"

        if cache_path.exists():
            return cache_path

        chunks = self._split_text(clean)

        if len(chunks) == 1:
            comm = edge_tts.Communicate(chunks[0], self.VOICE)
            await comm.save(str(cache_path))
        else:
            # generate parts then concatenate (binary mp3 concat is valid)
            part_paths: list[Path] = []
            for i, chunk in enumerate(chunks):
                part_path = self.cache_dir / f"{cache_key}_p{i}.mp3"
                comm = edge_tts.Communicate(chunk, self.VOICE)
                await comm.save(str(part_path))
                part_paths.append(part_path)
            with open(cache_path, "wb") as out:
                for pp in part_paths:
                    out.write(pp.read_bytes())
                    pp.unlink()

        return cache_path
