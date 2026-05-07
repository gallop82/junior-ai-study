from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Junior AI Study"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    sqlite_db_path: str = "data/app.db"
    generated_dir: str = "generated"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def backend_root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def app_root(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def data_dir(self) -> Path:
        return self.app_root / "data"

    @property
    def skills_dir(self) -> Path:
        return self.data_dir / "skills"

    @property
    def teachers_dir(self) -> Path:
        return self.data_dir / "teachers"

    @property
    def sqlite_path(self) -> Path:
        path = Path(self.sqlite_db_path)
        if not path.is_absolute():
            return self.backend_root / path
        return path

    @property
    def generated_path(self) -> Path:
        path = Path(self.generated_dir)
        if not path.is_absolute():
            return self.backend_root / path
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()

