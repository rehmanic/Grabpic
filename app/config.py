from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg2://grabpic:grabpic@127.0.0.1:5432/grabpic"
    storage_root: str = "./data/storage"
    insightface_model: str = "buffalo_l"
    # Persist InsightFace weights (e.g. /data/insightface in Docker). Env: INSIGHTFACE_ROOT.
    insightface_root: str | None = None
    match_threshold: float = 0.35
    selfie_auth_threshold: float = 0.32
    api_title: str = "Grabpic API"
    api_version: str = "1.0.0"
    # Kaggle slug for scripts/datasets_lfw.py (LFW mirror for demos).
    kaggle_lfw_dataset_slug: str = "jessicali9530/lfw-dataset"


@lru_cache
def get_settings() -> Settings:
    return Settings()
