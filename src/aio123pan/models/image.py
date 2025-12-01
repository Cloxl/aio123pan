"""Data models for image hosting operations."""

from pydantic import BaseModel, ConfigDict, Field


class ImageInfo(BaseModel):
    """Image hosting information."""

    model_config = ConfigDict(populate_by_name=True)

    file_id: int = Field(alias="fileID")
    direct_url: str = Field(alias="directUrl")
    filename: str
    size: int
    format: str = Field(default="")

    @property
    def size_mb(self) -> float:
        """Get image size in MB."""
        return self.size / (1024 * 1024)
