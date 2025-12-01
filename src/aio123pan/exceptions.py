"""Exceptions for 123Pan API client."""


class Pan123Error(Exception):
    """Base exception for all 123Pan API errors."""

    def __init__(self, message: str, code: int | None = None, trace_id: str | None = None) -> None:
        self.message = message
        self.code = code
        self.trace_id = trace_id
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.code is not None:
            parts.append(f"(code: {self.code})")
        if self.trace_id:
            parts.append(f"[trace_id: {self.trace_id}]")
        return " ".join(parts)


class APIError(Pan123Error):
    """Generic API error when code != 0."""


class NetworkError(Pan123Error):
    """Network-related errors (connection, timeout, etc)."""


class ValidationError(Pan123Error):
    """Request validation error (invalid parameters)."""


class AuthenticationError(Pan123Error):
    """Authentication failed (code = 401)."""


class TokenExpiredError(AuthenticationError):
    """Access token has expired."""


class InvalidCredentialsError(AuthenticationError):
    """Invalid client_id or client_secret."""


class PermissionDeniedError(Pan123Error):
    """Permission denied (code = 403)."""


class TokenLimitExceededError(AuthenticationError):
    """Token number has exceeded the limit.

    Occurs when too many login sessions are active.
    User needs to log out from other devices.
    """


class RateLimitError(Pan123Error):
    """Rate limit exceeded (code = 429).

    API has QPS (Queries Per Second) limits.
    """


class QPSLimitError(RateLimitError):
    """QPS limit exceeded for specific API."""


class ResourceError(Pan123Error):
    """Base exception for resource-related errors."""


class ResourceNotFoundError(ResourceError):
    """Resource not found (code = 404)."""


class FileNotFoundError(ResourceNotFoundError):
    """File or folder not found."""


class ShareNotFoundError(ResourceNotFoundError):
    """Share link not found."""


class TaskNotFoundError(ResourceNotFoundError):
    """Task (offline download/transcode) not found."""


class ResourceAlreadyExistsError(ResourceError):
    """Resource already exists (duplicate)."""


class DuplicateFileError(ResourceAlreadyExistsError):
    """File with same name already exists."""


class StorageError(Pan123Error):
    """Storage-related errors."""


class InsufficientStorageError(StorageError):
    """Insufficient storage space."""


class QuotaExceededError(StorageError):
    """Storage quota exceeded."""


class FileOperationError(Pan123Error):
    """Base exception for file operations."""


class UploadError(FileOperationError):
    """Upload operation error."""


class DownloadError(FileOperationError):
    """Download operation error."""


class InvalidFileNameError(FileOperationError):
    """Invalid file name (contains illegal characters or too long)."""


class FileSizeLimitError(FileOperationError):
    """File size exceeds limit."""


class InvalidFileTypeError(FileOperationError):
    """Invalid file type for the operation."""


class FileHashMismatchError(UploadError):
    """File hash verification failed during upload."""


class ShareError(Pan123Error):
    """Base exception for share operations."""


class InvalidSharePasswordError(ShareError):
    """Invalid share password."""


class ShareExpiredError(ShareError):
    """Share link has expired."""


class ShareLimitExceededError(ShareError):
    """Share limit exceeded (max 100 files per share)."""


class InvalidSharePeriodError(ShareError):
    """Invalid share period (must be 1, 7, 30, or 0 days)."""


class OfflineDownloadError(Pan123Error):
    """Base exception for offline download operations."""


class UnsupportedProtocolError(OfflineDownloadError):
    """Unsupported download protocol (only HTTP/HTTPS supported)."""


class OfflineTaskFailedError(OfflineDownloadError):
    """Offline download task failed."""


class InvalidDownloadUrlError(OfflineDownloadError):
    """Invalid download URL."""


class ImageError(Pan123Error):
    """Base exception for image hosting operations."""


class UnsupportedImageFormatError(ImageError):
    """Unsupported image format.

    Supported: png, gif, jpeg, tiff, webp, jpg, tif, svg, bmp
    """


class ImageSizeLimitError(ImageError):
    """Image size exceeds limit."""


class VideoTranscodeError(Pan123Error):
    """Base exception for video transcoding operations."""


class TranscodeTaskFailedError(VideoTranscodeError):
    """Video transcode task failed."""


class UnsupportedVideoFormatError(VideoTranscodeError):
    """Unsupported video format for transcoding."""


class InvalidResolutionError(VideoTranscodeError):
    """Invalid resolution for transcoding."""


class BatchOperationError(Pan123Error):
    """Base exception for batch operations."""


class BatchSizeLimitError(BatchOperationError):
    """Batch size exceeds limit (max 100 items)."""


class PartialBatchFailureError(BatchOperationError):
    """Some items in batch operation failed.

    Contains details about which items failed.
    """

    def __init__(
        self,
        message: str,
        failed_items: list[dict] | None = None,
        code: int | None = None,
        trace_id: str | None = None,
    ) -> None:
        super().__init__(message, code, trace_id)
        self.failed_items = failed_items or []


class DirectLinkError(Pan123Error):
    """Base exception for direct link operations."""


class DirectLinkNotAvailableError(DirectLinkError):
    """Direct link not available for this file."""


class DirectLinkExpiredError(DirectLinkError):
    """Direct link has expired."""


class ServerError(Pan123Error):
    """Server-side error (code >= 500)."""


class InternalServerError(ServerError):
    """Internal server error (code = 500)."""


class ServiceUnavailableError(ServerError):
    """Service temporarily unavailable (code = 503)."""


class GatewayTimeoutError(ServerError):
    """Gateway timeout (code = 504)."""
