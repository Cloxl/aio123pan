"""Data models for offline download operations."""

from pydantic import BaseModel, ConfigDict, Field


class OfflineTaskInfo(BaseModel):
    """Offline download task information."""

    model_config = ConfigDict(populate_by_name=True)

    task_id: int = Field(alias="taskID")
    status: int
    progress: int = Field(default=0)
    fail_reason: str = Field(alias="failReason", default="")
    file_id: int | None = Field(alias="fileID", default=None)
    url: str = Field(default="")

    @property
    def is_success(self) -> bool:
        """Check if task completed successfully."""
        return self.status == 0

    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == 1

    @property
    def is_in_progress(self) -> bool:
        """Check if task is in progress."""
        return self.status == 2


class CreateOfflineTaskResponse(BaseModel):
    """Response model for create offline download task."""

    model_config = ConfigDict(populate_by_name=True)

    task_id: int = Field(alias="taskID")
