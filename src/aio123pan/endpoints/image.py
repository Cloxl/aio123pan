"""Image hosting endpoint."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from aio123pan.exceptions import UnsupportedImageFormatError
from aio123pan.models.image import ImageInfo

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class ImageEndpoint:
    """Image hosting related endpoints."""

    SUPPORTED_FORMATS = {"png", "gif", "jpeg", "jpg", "tiff", "tif", "webp", "svg", "bmp"}

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def upload_image(
        self,
        file_path: str | Path,
        dir_id: int | None = None,
    ) -> ImageInfo:
        """Upload an image to image hosting.

        Note: This API may return 404 and require special account permissions or features.

        Args:
            file_path: Path to image file
            dir_id: Optional directory ID to upload to

        Returns:
            ImageInfo containing file_id and direct_url

        Raises:
            ResourceNotFoundError: If API endpoint is not available
            UnsupportedImageFormatError: If image format is not supported
        """
        file_path = Path(file_path)
        file_format = file_path.suffix.lstrip(".").lower()

        if file_format not in self.SUPPORTED_FORMATS:
            raise UnsupportedImageFormatError(
                f"Unsupported image format: {file_format}. "
                f"Supported formats: {', '.join(sorted(self.SUPPORTED_FORMATS))}",
            )

        payload: dict[str, str | int] = {
            "fileName": file_path.name,
        }

        if dir_id is not None:
            payload["dirID"] = dir_id

        with open(file_path, "rb") as f:
            image_data = f.read()

        files = {"file": (file_path.name, image_data, f"image/{file_format}")}

        data = await self.client._request(
            "POST",
            "/api/v1/image/upload",
            files=files,
            data=payload,
        )
        return ImageInfo.model_validate(data)

    async def copy_cloud_image(self, file_id: int) -> str:
        """Copy an existing cloud file to image hosting and get direct link.

        Note: This API may return 404 and require special account permissions or features.

        Args:
            file_id: File ID of the image in cloud storage

        Returns:
            Direct URL of the image

        Raises:
            ResourceNotFoundError: If API endpoint is not available
        """
        data = await self.client.post("/api/v1/image/copy", json={"fileID": file_id})
        return data.get("directUrl", "")
