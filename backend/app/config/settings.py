
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "Enterprise AI Knowledge Assistant"
    ENVIRONMENT: Literal["local", "development", "production"] = "local"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/knowledge_assistant"
    )

    # --- Auth / JWT ---
    JWT_SECRET_KEY: str = Field(default="change-me-in-env")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # --- Vector Store ---
    CHROMA_PERSIST_DIR: str = "./chroma_store"

    # --- Embeddings ---
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # --- LLM Providers ---
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    PRIMARY_LLM_PROVIDER: Literal["gemini", "groq"] = "groq"

    # --- RAG defaults ---
    DEFAULT_CHUNK_SIZE: int = 1000
    DEFAULT_CHUNK_OVERLAP: int = 150
    DEFAULT_TOP_K: int = 5

    # --- File Uploads ---
    MAX_UPLOAD_SIZE_MB: int = 20
    UPLOAD_DIR: str = "./uploads"


@lru_cache
def get_settings() -> Settings:
    """Cached — .env parsed once per process, not on every import/request."""
    return Settings()


settings = get_settings()
