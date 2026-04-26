"""Application configuration using pydantic-settings for environment-based config."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Digital Ophthalmology Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str | None = None

    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # ML Model
    model_path: Path | None = None

    # File Upload
    upload_dir: Path | None = None
    max_upload_size_mb: int = 10
    allowed_extensions: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    @property
    def resolved_model_path(self) -> Path:
        """Get the resolved model path, defaulting to the standard location."""
        if self.model_path:
            return self.model_path
        return Path(__file__).resolve().parents[2] / "models" / "eye_disease_final_cropped.keras"

    @property
    def resolved_upload_dir(self) -> Path:
        """Get the resolved upload directory, defaulting to the standard location."""
        if self.upload_dir:
            return self.upload_dir
        return Path(__file__).resolve().parents[2] / "uploads"

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()