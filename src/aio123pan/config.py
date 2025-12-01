"""Configuration management for 123Pan client."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Pan123Settings(BaseSettings):
    """Settings for 123Pan client with support for environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="PAN123_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    client_id: str | None = Field(default=None, description="123Pan client ID")
    client_secret: str | None = Field(default=None, description="123Pan client secret")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    base_url: str = Field(default="https://open-api.123pan.com", description="API base URL")
    enable_token_storage: bool = Field(default=False, description="Enable automatic token persistence to .env file")


def get_settings() -> Pan123Settings:
    """Get settings instance with environment variables loaded."""
    return Pan123Settings()
