from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union, Optional, Any
import json


class Settings(BaseSettings):
    environment: str = "development"
    cors_origins: Union[List[str], str] = ["http://localhost:3000"]
    frontend_url: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-3.5-flash"
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_storage_bucket: str = "ventureos-documents"

    # RAG & Embeddings
    embedding_provider: str = "gemini"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768
    chunk_size: int = 600
    chunk_overlap: int = 100
    rag_top_k: int = 5

    # Reliability & Production Hardening (Phase 8 + 9)
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 3
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_file_extensions: List[str] = [".pdf", ".docx", ".txt", ".md"]

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [item.strip() for item in v_stripped.split(",") if item.strip()]
    def model_post_init(self, __context: Any) -> None:
        if self.frontend_url:
            clean_url = self.frontend_url.strip()
            if clean_url and clean_url not in self.cors_origins:
                self.cors_origins.append(clean_url)

    def validate_production_config(self) -> None:
        """
        Validates that required production keys are set.
        Never reveals secret values in error messages.
        """
        missing = []
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_key:
            missing.append("SUPABASE_KEY")

        if missing and self.environment == "production":
            raise RuntimeError(
                f"Required application configuration is missing: {', '.join(missing)}"
            )

    @property
    def masked_gemini_key(self) -> str:
        if not self.gemini_api_key:
            return "NOT_SET"
        return f"{self.gemini_api_key[:6]}...{self.gemini_api_key[-4:]}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
settings.validate_production_config()
