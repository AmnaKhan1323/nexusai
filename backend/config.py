"""
NexusAI — Configuration Management
Loads settings from environment variables with validation.
Fully free: uses Ollama (local LLM) + ChromaDB (local vector DB).
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama (Free, local LLM)
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    llm_model: str = Field(default="llama3", env="LLM_MODEL")
    embedding_model: str = Field(default="nomic-embed-text", env="EMBEDDING_MODEL")

    # ChromaDB (Free, local vector DB)
    chroma_persist_dir: str = Field(default="./chroma_data", env="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field(default="nexusai_documents", env="CHROMA_COLLECTION_NAME")

    # Database
    database_url: str = Field(
        default="postgresql://nexusai:nexusai_secret@localhost:5432/nexusai_db",
        env="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # App
    app_env: str = Field(default="development", env="APP_ENV")
    app_debug: bool = Field(default=True, env="APP_DEBUG")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="CORS_ORIGINS",
    )
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")

    # Chunking
    chunk_size: int = Field(default=512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")

    # LLM Settings
    max_context_tokens: int = Field(default=3000, env="MAX_CONTEXT_TOKENS")
    temperature: float = Field(default=0.1, env="TEMPERATURE")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
