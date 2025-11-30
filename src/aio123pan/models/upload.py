"""Data models for upload operations."""


from pydantic import BaseModel, ConfigDict, Field


class CreateFileResponse(BaseModel):
    """Response model for file creation."""

    model_config = ConfigDict(populate_by_name=True)

    reuse: bool
    file_id: int | None = Field(alias="fileID", default=None)
    preupload_id: str | None = Field(alias="preuploadID", default=None)
    slice_size: int | None = Field(alias="sliceSize", default=None)
    servers: list[str] = Field(default_factory=list)

    @property
    def is_rapid_upload(self) -> bool:
        """Check if file was uploaded via rapid upload (seconds upload)."""
        return self.reuse


class UploadCompleteResponse(BaseModel):
    """Response model for upload completion."""

    model_config = ConfigDict(populate_by_name=True)

    completed: bool
    file_id: int = Field(alias="fileID", default=0)


class UploadDomainResponse(BaseModel):
    """Response model for upload domain."""

    servers: list[str] = Field(default_factory=list)
