"""Folder endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class FolderEndpoint:
    """Folder operations related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def create_folder(self, parent_file_id: int, name: str) -> int:
        """Create a new folder.

        Args:
            parent_file_id: Parent folder ID, 0 for root directory
            name: Folder name

        Returns:
            Created folder ID
        """
        from aio123pan.validators import validate_filename

        validate_filename(name)

        data = await self.client.post("/upload/v1/file/mkdir", json={"parentID": parent_file_id, "name": name})
        return data.get("dirID", 0)
