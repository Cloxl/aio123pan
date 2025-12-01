"""Core client for 123Pan API."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from aio123pan.endpoints.auth import AuthEndpoint
    from aio123pan.endpoints.direct_link import DirectLinkEndpoint
    from aio123pan.endpoints.file import FileEndpoint
    from aio123pan.endpoints.folder import FolderEndpoint
    from aio123pan.endpoints.image import ImageEndpoint
    from aio123pan.endpoints.offline import OfflineEndpoint
    from aio123pan.endpoints.share import ShareEndpoint
    from aio123pan.endpoints.trash import TrashEndpoint
    from aio123pan.endpoints.upload import UploadEndpoint
    from aio123pan.endpoints.user import UserEndpoint
    from aio123pan.endpoints.video import VideoEndpoint

from aio123pan.config import get_settings
from aio123pan.constants import CONTENT_TYPE, PLATFORM
from aio123pan.exceptions import APIError, AuthenticationError, NetworkError, RateLimitError
from aio123pan.storage import TokenStorage
from aio123pan.types import JSONDict


class Pan123Client:
    """Async client for 123Pan Open API.

    Example:
        # Auto-load from environment variables
        async with Pan123Client() as client:
            user = await client.user.get_user_info()

        # Or provide credentials explicitly
        async with Pan123Client(
            client_id="your_id",
            client_secret="your_secret"
        ) as client:
            user = await client.user.get_user_info()
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
        expired_at: datetime | None = None,
        timeout: float | None = None,
        base_url: str | None = None,
        enable_token_storage: bool | None = None,
        env_file: str | Path | None = None,
    ) -> None:
        settings = get_settings()

        self.client_id = client_id or settings.client_id
        self.client_secret = client_secret or settings.client_secret
        self._timeout = timeout if timeout is not None else settings.timeout
        self._base_url = base_url or settings.base_url

        self._enable_token_storage = (
            enable_token_storage if enable_token_storage is not None else settings.enable_token_storage
        )
        self._token_storage = TokenStorage(env_file) if self._enable_token_storage else None

        if access_token and expired_at:
            self._access_token = access_token
            self._expired_at = expired_at
        elif self._token_storage and (token_data := self._token_storage.load()):
            self._access_token = token_data.access_token
            self._expired_at = token_data.expired_at
        else:
            self._access_token = None
            self._expired_at = None

        self._client: httpx.AsyncClient | None = None
        self._auth_endpoint = None
        self._user_endpoint = None
        self._file_endpoint = None
        self._folder_endpoint = None
        self._upload_endpoint = None
        self._trash_endpoint = None
        self._share_endpoint = None
        self._offline_endpoint = None
        self._image_endpoint = None
        self._direct_link_endpoint = None
        self._video_endpoint = None

    async def __aenter__(self) -> Pan123Client:
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    @property
    def auth(self) -> AuthEndpoint:
        """Get authentication endpoint."""
        if self._auth_endpoint is None:
            from aio123pan.endpoints.auth import AuthEndpoint

            self._auth_endpoint = AuthEndpoint(self)
        return self._auth_endpoint

    @property
    def user(self) -> UserEndpoint:
        """Get user endpoint."""
        if self._user_endpoint is None:
            from aio123pan.endpoints.user import UserEndpoint

            self._user_endpoint = UserEndpoint(self)
        return self._user_endpoint

    @property
    def file(self) -> FileEndpoint:
        """Get file endpoint."""
        if self._file_endpoint is None:
            from aio123pan.endpoints.file import FileEndpoint

            self._file_endpoint = FileEndpoint(self)
        return self._file_endpoint

    @property
    def folder(self) -> FolderEndpoint:
        """Get folder endpoint."""
        if self._folder_endpoint is None:
            from aio123pan.endpoints.folder import FolderEndpoint

            self._folder_endpoint = FolderEndpoint(self)
        return self._folder_endpoint

    @property
    def upload(self) -> UploadEndpoint:
        """Get upload endpoint."""
        if self._upload_endpoint is None:
            from aio123pan.endpoints.upload import UploadEndpoint

            self._upload_endpoint = UploadEndpoint(self)
        return self._upload_endpoint

    @property
    def trash(self) -> TrashEndpoint:
        """Get trash endpoint."""
        if self._trash_endpoint is None:
            from aio123pan.endpoints.trash import TrashEndpoint

            self._trash_endpoint = TrashEndpoint(self)
        return self._trash_endpoint

    @property
    def share(self) -> ShareEndpoint:
        """Get share endpoint."""
        if self._share_endpoint is None:
            from aio123pan.endpoints.share import ShareEndpoint

            self._share_endpoint = ShareEndpoint(self)
        return self._share_endpoint

    @property
    def offline(self) -> OfflineEndpoint:
        """Get offline download endpoint."""
        if self._offline_endpoint is None:
            from aio123pan.endpoints.offline import OfflineEndpoint

            self._offline_endpoint = OfflineEndpoint(self)
        return self._offline_endpoint

    @property
    def image(self) -> ImageEndpoint:
        """Get image hosting endpoint."""
        if self._image_endpoint is None:
            from aio123pan.endpoints.image import ImageEndpoint

            self._image_endpoint = ImageEndpoint(self)
        return self._image_endpoint

    @property
    def direct_link(self) -> DirectLinkEndpoint:
        """Get direct link endpoint."""
        if self._direct_link_endpoint is None:
            from aio123pan.endpoints.direct_link import DirectLinkEndpoint

            self._direct_link_endpoint = DirectLinkEndpoint(self)
        return self._direct_link_endpoint

    @property
    def video(self) -> VideoEndpoint:
        """Get video transcoding endpoint."""
        if self._video_endpoint is None:
            from aio123pan.endpoints.video import VideoEndpoint

            self._video_endpoint = VideoEndpoint(self)
        return self._video_endpoint

    async def _ensure_client(self) -> None:
        """Ensure httpx client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=httpx.Timeout(self._timeout),
                headers={
                    "Platform": PLATFORM,
                    "Content-Type": CONTENT_TYPE,
                },
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def is_token_valid(self) -> bool:
        """Check if access token is valid."""
        if not self._access_token or not self._expired_at:
            return False
        return datetime.now(timezone.utc) < self._expired_at

    async def _ensure_authenticated(self) -> None:
        """Ensure client is authenticated."""
        if not self.is_token_valid:
            if not self.client_id or not self.client_secret:
                raise AuthenticationError("Client ID and Secret required for authentication")
            await self._refresh_token()

    async def _refresh_token(self) -> None:
        """Refresh access token."""
        if not self.client_id or not self.client_secret:
            raise AuthenticationError("Client ID and Secret required for token refresh")

        from aio123pan.endpoints.auth import AuthEndpoint

        auth = AuthEndpoint(self)
        token_data = await auth.get_access_token(self.client_id, self.client_secret)
        self._access_token = token_data.access_token
        self._expired_at = token_data.expired_at

        if self._token_storage:
            self._token_storage.save(self._access_token, self._expired_at)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        require_auth: bool = True,
        json: JSONDict | None = None,
        params: JSONDict | None = None,
        **kwargs: Any,
    ) -> JSONDict:
        """Make HTTP request to API."""
        await self._ensure_client()

        if require_auth:
            await self._ensure_authenticated()

        headers = kwargs.pop("headers", {})
        if require_auth and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            response = await self._client.request(
                method=method, url=path, json=json, params=params, headers=headers, **kwargs
            )
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}") from e

        try:
            data = response.json()
        except Exception:
            if response.status_code >= 400:
                return self._handle_response({
                    "code": response.status_code,
                    "message": response.text or f"HTTP {response.status_code}",
                })
            raise NetworkError("Failed to parse response as JSON") from None

        if response.status_code >= 400:
            return self._handle_response({"code": response.status_code, "message": data.get("message", response.text)})

        return self._handle_response(data)

    def _handle_response(self, data: JSONDict) -> JSONDict:
        """Handle API response and raise appropriate exceptions."""
        from aio123pan.exceptions import (
            FileNotFoundError,
            GatewayTimeoutError,
            InsufficientStorageError,
            InternalServerError,
            InvalidCredentialsError,
            PermissionDeniedError,
            QPSLimitError,
            QuotaExceededError,
            ResourceNotFoundError,
            ServerError,
            ServiceUnavailableError,
            ShareNotFoundError,
            TaskNotFoundError,
            TokenExpiredError,
            TokenLimitExceededError,
        )

        code = data.get("code", -1)
        message = data.get("message", "Unknown error")
        trace_id = data.get("x-traceID")
        message_lower = message.lower()

        if code == 0:
            return data.get("data", {})

        if code == 401:
            self._access_token = None
            self._expired_at = None
            if self._token_storage:
                self._token_storage.clear()

            if "expired" in message_lower:
                raise TokenExpiredError(message, code=code, trace_id=trace_id)
            if "invalid" in message_lower and ("client" in message_lower or "credential" in message_lower):
                raise InvalidCredentialsError(message, code=code, trace_id=trace_id)
            if "token" in message_lower and "exceeded" in message_lower:
                raise TokenLimitExceededError(message, code=code, trace_id=trace_id)

            raise AuthenticationError(message, code=code, trace_id=trace_id)

        if code == 403:
            raise PermissionDeniedError(message, code=code, trace_id=trace_id)

        if code == 404:
            if "file" in message_lower:
                raise FileNotFoundError(message, code=code, trace_id=trace_id)
            if "share" in message_lower:
                raise ShareNotFoundError(message, code=code, trace_id=trace_id)
            if "task" in message_lower:
                raise TaskNotFoundError(message, code=code, trace_id=trace_id)
            raise ResourceNotFoundError(message, code=code, trace_id=trace_id)

        if code == 429:
            if "qps" in message_lower:
                raise QPSLimitError(message, code=code, trace_id=trace_id)
            raise RateLimitError(message, code=code, trace_id=trace_id)

        if code >= 500:
            if code == 500:
                raise InternalServerError(message, code=code, trace_id=trace_id)
            if code == 503:
                raise ServiceUnavailableError(message, code=code, trace_id=trace_id)
            if code == 504:
                raise GatewayTimeoutError(message, code=code, trace_id=trace_id)
            raise ServerError(message, code=code, trace_id=trace_id)

        if "storage" in message_lower or "space" in message_lower:
            if "insufficient" in message_lower or "not enough" in message_lower:
                raise InsufficientStorageError(message, code=code, trace_id=trace_id)
            if "quota" in message_lower or "exceed" in message_lower:
                raise QuotaExceededError(message, code=code, trace_id=trace_id)

        raise APIError(message, code=code, trace_id=trace_id)

    async def get(self, path: str, **kwargs: Any) -> JSONDict:
        """Make GET request."""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> JSONDict:
        """Make POST request."""
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> JSONDict:
        """Make PUT request."""
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> JSONDict:
        """Make DELETE request."""
        return await self._request("DELETE", path, **kwargs)
