"""123Pan async API client."""

from aio123pan.client import Pan123Client
from aio123pan.exceptions import (
    APIError,
    AuthenticationError,
    DownloadError,
    ImageError,
    InsufficientStorageError,
    InvalidSharePeriodError,
    NetworkError,
    OfflineDownloadError,
    Pan123Error,
    PermissionDeniedError,
    RateLimitError,
    ResourceNotFoundError,
    ShareError,
    ShareLimitExceededError,
    TokenExpiredError,
    TokenLimitExceededError,
    UnsupportedImageFormatError,
    UnsupportedProtocolError,
    UploadError,
    ValidationError,
    VideoTranscodeError,
)

try:
    from aio123pan._version import __version__, __version_tuple__
except ImportError:
    __version__ = "unknown"
    __version_tuple__ = (0, 0, 0, "unknown", 0)

__all__ = [
    "Pan123Client",
    "Pan123Error",
    "APIError",
    "AuthenticationError",
    "TokenExpiredError",
    "TokenLimitExceededError",
    "PermissionDeniedError",
    "RateLimitError",
    "ValidationError",
    "NetworkError",
    "ResourceNotFoundError",
    "InsufficientStorageError",
    "UploadError",
    "DownloadError",
    "ShareError",
    "ShareLimitExceededError",
    "InvalidSharePeriodError",
    "OfflineDownloadError",
    "UnsupportedProtocolError",
    "ImageError",
    "UnsupportedImageFormatError",
    "VideoTranscodeError",
    "__version__",
    "__version_tuple__",
]
