"""Data models for file operations."""

from pydantic import BaseModel, ConfigDict, Field


class FileInfo(BaseModel):
    """File or folder information."""

    model_config = ConfigDict(populate_by_name=True)

    file_id: int = Field(alias="fileId")
    filename: str
    type: int
    size: int
    etag: str
    status: int
    parent_file_id: int = Field(alias="parentFileId")
    category: int
    trashed: bool = Field(default=False)

    @property
    def is_folder(self) -> bool:
        """Check if this is a folder."""
        return self.type == 1

    @property
    def is_file(self) -> bool:
        """Check if this is a file."""
        return self.type == 0


class FileListResponse(BaseModel):
    """Response model for file list."""

    model_config = ConfigDict(populate_by_name=True)

    last_file_id: int = Field(alias="lastFileId")
    file_list: list[FileInfo] = Field(alias="fileList", default_factory=list)

    @property
    def has_more(self) -> bool:
        """Check if there are more files to fetch."""
        return self.last_file_id != -1
