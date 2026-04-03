from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str
    sync_database_url: str
    redis_url: str
    jwt_secret: str
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    openai_api_key: str | None = None
    crawler_concurrency: int = 20
    crawler_max_retries: int = 5
    crawler_default_region: str = "IN"
    enable_ai_generation: bool = True
    enable_rate_limiting: bool = True
    bootstrap_admin_email: str = "admin@atlasbi.local"
    bootstrap_admin_password: str = "AtlasBI-Admin-2026"
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    embedding_dimensions: int = 1536
    hosted_embedding_model: str | None = None
    hosted_rerank_model: str | None = None
    stripe_secret_key: str | None = None
    stripe_public_key: str | None = None
    stripe_webhook_secret: str | None = None
    serpapi_api_key: str | None = None
    hunter_api_key: str | None = None
    peopledatalabs_api_key: str | None = None
    frontend_app_url: str = "http://localhost:3000"
    discovery_provider: str = "hybrid"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
