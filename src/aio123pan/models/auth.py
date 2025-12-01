"""Data models for authentication."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccessTokenResponse(BaseModel):
    """Response model for access token."""

    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    expired_at: datetime = Field(alias="expiredAt")
