"""Data models for video transcoding operations."""

from pydantic import BaseModel, ConfigDict, Field


class TranscodeTaskInfo(BaseModel):
    """Video transcode task information."""

    model_config = ConfigDict(populate_by_name=True)

    task_id: int = Field(alias="taskID")
    file_id: int = Field(alias="fileID")
    status: int
    progress: int = Field(default=0)
    resolution: str = Field(default="")
    format: str = Field(default="")
    play_url: str | None = Field(alias="playUrl", default=None)

    @property
    def is_queued(self) -> bool:
        """Check if task is queued."""
        return self.status == 0

    @property
    def is_in_progress(self) -> bool:
        """Check if task is in progress."""
        return self.status == 1

    @property
    def is_success(self) -> bool:
        """Check if task completed successfully."""
        return self.status == 2

    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == 3


class CreateTranscodeTaskResponse(BaseModel):
    """Response model for create transcode task."""

    model_config = ConfigDict(populate_by_name=True)

    task_id: int = Field(alias="taskID")
