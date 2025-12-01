"""Upload endpoint."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from aio123pan.exceptions import UploadError
from aio123pan.models.upload import CreateFileResponse, UploadCompleteResponse, UploadDomainResponse
from aio123pan.utils import calculate_md5, calculate_md5_from_bytes

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class UploadEndpoint:
    """Upload related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def get_upload_domain(self) -> UploadDomainResponse:
        """Get upload domain servers.

        Returns:
            UploadDomainResponse with available upload servers
        """
        data = await self.client.get("/upload/v2/file/upload_domain")
        return UploadDomainResponse.model_validate(data)

    async def create_file(
        self,
        parent_file_id: int,
        filename: str,
        etag: str,
        size: int,
        duplicate: int | None = None,
        contain_dir: bool = False,
    ) -> CreateFileResponse:
        """Create file for upload (step 1 of multipart upload).

        Args:
            parent_file_id: Parent folder ID
            filename: File name (or path+filename if contain_dir=True)
            etag: MD5 hash of the file
            size: File size in bytes
            duplicate: File handling strategy (1=keep both, 2=overwrite)
            contain_dir: Whether filename contains path (auto-creates directories)

        Returns:
            CreateFileResponse with upload information
        """
        from aio123pan.validators import validate_filename

        if not contain_dir:
            validate_filename(filename)

        payload = {
            "parentFileID": parent_file_id,
            "filename": filename,
            "etag": etag,
            "size": size,
        }
        if duplicate is not None:
            payload["duplicate"] = duplicate
        if contain_dir:
            payload["containDir"] = contain_dir

        data = await self.client.post("/upload/v2/file/create", json=payload)
        return CreateFileResponse.model_validate(data)

    async def upload_slice(
        self,
        server: str,
        preupload_id: str,
        slice_no: int,
        slice_data: bytes,
        slice_md5: str,
    ) -> bool:
        """Upload a single slice (step 2 of multipart upload).

        Args:
            server: Upload server URL
            preupload_id: Preupload ID from create_file
            slice_no: Slice number (starts from 1)
            slice_data: Slice data bytes
            slice_md5: MD5 hash of the slice

        Returns:
            True if upload was successful
        """
        await self.client._ensure_client()

        # Manually construct multipart/form-data body like official Python example
        import uuid

        boundary = uuid.uuid4().hex
        parts = []

        # Add form fields
        for field_name, field_value in [
            ("preuploadID", preupload_id),
            ("sliceNo", str(slice_no)),
            ("sliceMD5", slice_md5),
        ]:
            parts.append(f"--{boundary}\r\n".encode())
            parts.append(f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'.encode())
            parts.append(f"{field_value}\r\n".encode())

        # Add file field
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="slice"; filename="slice_{slice_no}"\r\n'.encode())
        parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
        parts.append(slice_data)
        parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())

        body = b"".join(parts)

        headers = {
            "Platform": "open_platform",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
        if self.client._access_token:
            headers["Authorization"] = f"Bearer {self.client._access_token}"

        if self.client._client is None:
            raise RuntimeError("HTTP client not initialized")

        response = await self.client._client.post(
            f"{server}/upload/v2/file/slice",
            content=body,
            headers=headers,
        )
        response.raise_for_status()

        result = response.json()
        if result.get("code") != 0:
            raise UploadError(f"Upload slice failed: {result.get('message')}")

        return True

    async def upload_complete(self, preupload_id: str) -> UploadCompleteResponse:
        """Notify server that upload is complete (step 3 of multipart upload).

        Args:
            preupload_id: Preupload ID from create_file

        Returns:
            UploadCompleteResponse with completion status
        """
        data = await self.client.post(
            "/upload/v2/file/upload_complete",  # Fixed: upload_complete not upload/complete
            json={"preuploadID": preupload_id},
        )
        return UploadCompleteResponse.model_validate(data)

    async def upload_file(
        self,
        file_path: str | Path,
        parent_file_id: int = 0,
        filename: str | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
        duplicate: int | None = None,
    ) -> int:
        """Upload a file with automatic slice handling.

        Args:
            file_path: Path to the file to upload
            parent_file_id: Parent folder ID (default: 0 for root)
            filename: Custom filename (default: use original filename)
            progress_callback: Optional callback function(current, total) for progress
            duplicate: File handling strategy (1=keep both, 2=overwrite)

        Returns:
            File ID of the uploaded file
        """
        from aio123pan.validators import validate_file_size, validate_filename

        file_path = Path(file_path)
        validate_file_size(file_path)

        if filename is None:
            filename = file_path.name

        validate_filename(filename)

        file_size = file_path.stat().st_size
        file_md5 = calculate_md5(file_path)

        create_response = await self.create_file(
            parent_file_id=parent_file_id,
            filename=filename,
            etag=file_md5,
            size=file_size,
            duplicate=duplicate,
        )

        if create_response.is_rapid_upload:
            return create_response.file_id or 0

        if not create_response.preupload_id or not create_response.slice_size:
            raise UploadError("Invalid upload response: missing preupload_id or slice_size")

        slice_size = create_response.slice_size
        server = create_response.servers[0] if create_response.servers else "https://open-api.123pan.com"

        with open(file_path, "rb") as f:
            slice_no = 1
            uploaded_bytes = 0

            while True:
                slice_data = f.read(slice_size)
                if not slice_data:
                    break

                slice_md5 = calculate_md5_from_bytes(slice_data)

                await self.upload_slice(
                    server=server,
                    preupload_id=create_response.preupload_id,
                    slice_no=slice_no,
                    slice_data=slice_data,
                    slice_md5=slice_md5,
                )

                uploaded_bytes += len(slice_data)
                if progress_callback:
                    progress_callback(uploaded_bytes, file_size)

                slice_no += 1

        max_retries = 10
        for _ in range(max_retries):
            try:
                complete_response = await self.upload_complete(create_response.preupload_id)

                if complete_response.completed and complete_response.file_id:
                    return complete_response.file_id

                await asyncio.sleep(1)
            except Exception as e:
                # Handle file verification in progress error (code: 20103)
                error_msg = str(e)
                if "校验中" in error_msg or "20103" in error_msg:
                    await asyncio.sleep(1)
                    continue
                raise

        raise UploadError(f"Upload completion timed out after {max_retries} attempts")
