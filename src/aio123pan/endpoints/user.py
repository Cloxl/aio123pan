"""User endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aio123pan.models.user import UserInfo

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class UserEndpoint:
    """User information related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def get_user_info(self) -> UserInfo:
        """Get current user information.

        Returns:
            UserInfo object with user details
        """
        data = await self.client.get("/api/v1/user/info")
        return UserInfo.model_validate(data)
