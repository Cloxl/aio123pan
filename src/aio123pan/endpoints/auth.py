"""Authentication endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aio123pan.models.auth import AccessTokenResponse

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class AuthEndpoint:
    """Authentication related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def get_access_token(self, client_id: str, client_secret: str) -> AccessTokenResponse:
        """Get access token.

        Args:
            client_id: Client ID from 123Pan developer platform
            client_secret: Client Secret from 123Pan developer platform

        Returns:
            AccessTokenResponse with token and expiration time
        """
        data = await self.client.post(
            "/api/v1/access_token",
            json={"clientID": client_id, "clientSecret": client_secret},
            require_auth=False,
        )
        return AccessTokenResponse.model_validate(data)
