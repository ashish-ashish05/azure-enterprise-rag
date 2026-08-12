from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "enterprise-rag"
    app_env: str = "development"
    log_level: str = "INFO"

    azure_openai_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str | None = Field(
        default=None,
        alias="AZURE_OPENAI_API_KEY",
    )
    azure_openai_chat_deployment: str = Field(
        ...,
        alias="AZURE_OPENAI_CHAT_DEPLOYMENT",
    )
    azure_openai_embedding_deployment: str = Field(
        ...,
        alias="AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
    )

    azure_search_endpoint: str = Field(
        ...,
        alias="AZURE_SEARCH_ENDPOINT",
    )
    azure_search_api_key: str | None = Field(
        default=None,
        alias="AZURE_SEARCH_API_KEY",
    )
    azure_search_index_name: str = Field(
        default="enterprise-rag-index",
        alias="AZURE_SEARCH_INDEX_NAME",
    )

    azure_storage_account_url: str = Field(
        ...,
        alias="AZURE_STORAGE_ACCOUNT_URL",
    )
    azure_storage_container: str = Field(
        default="knowledge-base",
        alias="AZURE_STORAGE_CONTAINER",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()