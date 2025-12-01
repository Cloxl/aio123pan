"""Offline download endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aio123pan.exceptions import UnsupportedProtocolError
from aio123pan.models.offline import CreateOfflineTaskResponse, OfflineTaskInfo

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class OfflineEndpoint:
    """Offline download related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def create_download_task(
        self,
        url: str,
        file_name: str | None = None,
        dir_id: int | None = None,
        callback_url: str | None = None,
    ) -> int:
        """Create an offline download task.

        Args:
            url: Download URL (HTTP/HTTPS only)
            file_name: Optional custom file name (must include extension)
            dir_id: Optional directory ID to download to
            callback_url: Optional callback URL for task completion notification

        Returns:
            Task ID for querying progress

        Note:
            - Only HTTP/HTTPS protocols are supported
            - Cannot download to root directory (dir_id=0)
            - Default download location: "来自:离线下载" folder
        """
        if not url.startswith(("http://", "https://")):
            raise UnsupportedProtocolError(
                f"Only HTTP/HTTPS protocols are supported, got: {url[:20]}...",
            )

        payload: dict[str, str | int] = {"url": url}

        if file_name is not None:
            payload["fileName"] = file_name
        if dir_id is not None:
            payload["dirID"] = dir_id
        if callback_url is not None:
            payload["callBackUrl"] = callback_url

        data = await self.client.post("/api/v1/offline/download", json=payload)
        response = CreateOfflineTaskResponse.model_validate(data)
        return response.task_id

    async def get_download_progress(self, task_id: int) -> OfflineTaskInfo:
        """Get offline download task progress.

        Args:
            task_id: Task ID returned from create_download_task

        Returns:
            OfflineTaskInfo containing task status and progress
        """
        data = await self.client.get("/api/v1/offline/progress", params={"taskID": task_id})
        return OfflineTaskInfo.model_validate(data)
