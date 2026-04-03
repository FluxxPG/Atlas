from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    database_url: str
    redis_url: str
    crawler_concurrency: int = 20
    crawler_max_retries: int = 5
    playwright_headless: bool = True
    playwright_timeout_ms: int = 30000
    embedding_dimensions: int = 1536
    openai_api_key: str | None = None
    hosted_embedding_model: str | None = None
    serpapi_api_key: str | None = None
    hunter_api_key: str | None = None
    peopledatalabs_api_key: str | None = None
    discovery_provider: str = "hybrid"
    approved_sources: str = "public_web,serpapi,india_local,google_business_profiles,google_maps,justdial,sulekha,tracxn,indiamart"
    fetch_directory_pages: bool = False
    directory_max_listing_pages: int = 3
    directory_max_detail_pages: int = 4


settings = Settings()
