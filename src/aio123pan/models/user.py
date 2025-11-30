"""Data models for user information."""

from pydantic import BaseModel, ConfigDict, Field


class UserInfo(BaseModel):
    """User information model."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="uid")
    nickname: str = Field(alias="nickname")
    space_used: int = Field(alias="spaceUse")
    space_capacity: int = Field(alias="spaceCapacity")
