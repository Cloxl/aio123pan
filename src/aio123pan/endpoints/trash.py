"""Trash (recycle bin) endpoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from aio123pan.models.file import FileInfo, FileListResponse

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class TrashEndpoint:
    """Trash (recycle bin) related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def list_trash(
        self,
        limit: int = 100,
        last_file_id: int | None = None,
    ) -> FileListResponse:
        """List files in trash.

        Note: 123Pan does not have a dedicated trash list API.
        This method uses the regular file list API and filters by trashed=1.

        Args:
            limit: Number of files per page, max 100
            last_file_id: Pagination parameter from previous response

        Returns:
            FileListResponse containing trashed files
        """
        from aio123pan.validators import validate_page_limit

        validate_page_limit(limit)

        params: dict[str, int] = {
            "parentFileId": 0,
            "limit": limit,
        }
        if last_file_id is not None:
            params["lastFileId"] = last_file_id

        # Use v2 file list API and filter by trashed field
        data = await self.client.get("/api/v2/file/list", params=params)
        response = FileListResponse.model_validate(data)

        # Filter only trashed files
        response.file_list = [f for f in response.file_list if f.trashed]

        return response

    async def list_all_trash(self, limit: int = 100) -> AsyncIterator[FileInfo]:
        """List all trashed files with automatic pagination.

        Args:
            limit: Number of files per page, max 100

        Yields:
            FileInfo objects
        """
        last_file_id = None
        while True:
            response = await self.list_trash(limit=limit, last_file_id=last_file_id)

            for file_info in response.file_list:
                yield file_info

            if not response.has_more:
                break

            last_file_id = response.last_file_id

    async def restore_file(self, file_id: int) -> bool:
        """Restore a file from trash.

        Note: This API may return 404 and require special account permissions.

        Args:
            file_id: File ID to restore

        Returns:
            True if restoration was successful

        Raises:
            ResourceNotFoundError: If API endpoint is not available
        """
        await self.client.post("/api/v1/file/trash/restore", json={"fileID": file_id})
        return True

    async def delete_permanently(self, file_id: int) -> bool:
        """Permanently delete a file from trash.

        Note: This API may return 404 and require special account permissions.

        Args:
            file_id: File ID to delete permanently

        Returns:
            True if deletion was successful

        Raises:
            ResourceNotFoundError: If API endpoint is not available
        """
        await self.client.post("/api/v1/file/trash/delete", json={"fileID": file_id})
        return True

    async def empty_trash(self) -> bool:
        """Empty the entire trash.

        Returns:
            True if operation was successful
        """
        await self.client.post("/api/v1/file/trash/empty")
        return True
