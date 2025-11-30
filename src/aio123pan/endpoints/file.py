"""File endpoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import TYPE_CHECKING

from aio123pan.models.file import FileInfo, FileListResponse

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class FileEndpoint:
    """File operations related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def list_files(
        self,
        parent_file_id: int = 0,
        limit: int = 100,
        last_file_id: int | None = None,
        search_data: str | None = None,
        search_mode: int = 0,
    ) -> FileListResponse:
        """List files in a directory (v2 API, recommended).

        Args:
            parent_file_id: Parent folder ID, 0 for root directory
            limit: Number of files per page, max 100
            last_file_id: Pagination parameter from previous response
            search_data: Search keyword
            search_mode: 0 for fuzzy search, 1 for exact match

        Returns:
            FileListResponse containing file list and pagination info
        """
        from aio123pan.validators import validate_page_limit

        validate_page_limit(limit)

        params = {
            "parentFileId": parent_file_id,
            "limit": limit,
        }
        if last_file_id is not None:
            params["lastFileId"] = last_file_id
        if search_data:
            params["searchData"] = search_data
            params["searchMode"] = search_mode

        data = await self.client.get("/api/v2/file/list", params=params)
        return FileListResponse.model_validate(data)

    async def list_all_files(
        self,
        parent_file_id: int = 0,
        limit: int = 100,
        search_data: str | None = None,
        search_mode: int = 0,
    ) -> AsyncIterator[FileInfo]:
        """List all files with automatic pagination.

        Args:
            parent_file_id: Parent folder ID, 0 for root directory
            limit: Number of files per page, max 100
            search_data: Search keyword
            search_mode: 0 for fuzzy search, 1 for exact match

        Yields:
            FileInfo objects
        """
        last_file_id = None
        while True:
            response = await self.list_files(
                parent_file_id=parent_file_id,
                limit=limit,
                last_file_id=last_file_id,
                search_data=search_data,
                search_mode=search_mode,
            )

            for file_info in response.file_list:
                yield file_info

            if not response.has_more:
                break

            last_file_id = response.last_file_id

    async def get_file_info(self, file_id: int) -> FileInfo:
        """Get file information by ID.

        Args:
            file_id: File ID

        Returns:
            FileInfo object
        """
        data = await self.client.get("/api/v1/file/info", params={"fileID": file_id})
        return FileInfo.model_validate(data)

    async def delete_file(self, file_id: int | list[int]) -> bool:
        """Delete file(s) or folder(s) (move to trash).

        Args:
            file_id: File ID or list of file IDs (max 100)

        Returns:
            True if deletion was successful
        """
        from aio123pan.validators import validate_batch_size

        file_ids = [file_id] if isinstance(file_id, int) else file_id
        validate_batch_size(len(file_ids), "delete")

        await self.client.post("/api/v1/file/trash", json={"fileIDs": file_ids})
        return True

    async def move_file(self, file_id: int | list[int], target_parent_id: int) -> bool:
        """Move file(s) or folder(s).

        Args:
            file_id: File ID or list of file IDs (max 100)
            target_parent_id: Target parent folder ID

        Returns:
            True if move was successful
        """
        from aio123pan.validators import validate_batch_size

        file_ids = [file_id] if isinstance(file_id, int) else file_id
        validate_batch_size(len(file_ids), "move")

        await self.client.post("/api/v1/file/move", json={"fileIDs": file_ids, "toParentFileID": target_parent_id})
        return True

    async def rename_file(self, file_id: int, new_name: str) -> bool:
        """Rename a file or folder.

        Args:
            file_id: File ID to rename
            new_name: New name

        Returns:
            True if rename was successful
        """
        from aio123pan.validators import validate_filename

        validate_filename(new_name)

        await self.client.put("/api/v1/file/name", json={"fileId": file_id, "fileName": new_name})
        return True

    async def copy_file(self, file_id: int, target_parent_id: int) -> int:
        """Copy a file or folder.

        Args:
            file_id: File ID to copy
            target_parent_id: Target parent folder ID

        Returns:
            New file ID
        """
        data = await self.client.post(
            "/api/v1/file/copy", json={"fileID": file_id, "targetParentID": target_parent_id}
        )
        return data.get("fileID", 0)

    async def download_file(self, file_id: int, save_path: str | Path | None = None) -> bytes | None:
        """Download a file.

        Args:
            file_id: File ID to download
            save_path: Optional path to save the file. If None, returns bytes.

        Returns:
            File bytes if save_path is None, otherwise None
        """
        download_info = await self.client.get("/api/v1/file/download_info", params={"fileID": file_id})
        download_url = download_info.get("DownloadURL")

        if not download_url:
            raise ValueError("No download URL available")

        await self.client._ensure_client()

        response = await self.client._client.get(download_url)
        response.raise_for_status()

        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)
            return None
        else:
            return response.content

