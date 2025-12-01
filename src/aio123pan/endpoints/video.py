"""Video transcoding endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aio123pan.models.video import CreateTranscodeTaskResponse, TranscodeTaskInfo

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class VideoEndpoint:
    """Video transcoding related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def create_transcode_task(
        self,
        file_id: int,
        resolution: str = "720p",
        format: str = "m3u8",
    ) -> int:
        """Create a video transcode task.

        Args:
            file_id: File ID of the video to transcode
            resolution: Target resolution (e.g., "720p", "1080p")
            format: Target format (e.g., "mp4", "m3u8")

        Returns:
            Task ID for querying transcode status
        """
        payload: dict[str, int | str] = {
            "fileID": file_id,
            "resolution": resolution,
            "format": format,
        }

        data = await self.client.post("/api/v1/video/transcode", json=payload)
        response = CreateTranscodeTaskResponse.model_validate(data)
        return response.task_id

    async def get_transcode_status(self, task_id: int) -> TranscodeTaskInfo:
        """Get video transcode task status.

        Args:
            task_id: Task ID returned from create_transcode_task

        Returns:
            TranscodeTaskInfo containing task status and progress
        """
        data = await self.client.get("/api/v1/video/transcode/status", params={"taskID": task_id})
        return TranscodeTaskInfo.model_validate(data)

    async def get_play_url(self, file_id: int) -> str:
        """Get play URL for a transcoded video.

        Args:
            file_id: File ID of the transcoded video

        Returns:
            Play URL for the video
        """
        data = await self.client.get("/api/v1/video/play", params={"fileID": file_id})
        return data.get("playUrl", "")
