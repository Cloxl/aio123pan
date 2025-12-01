"""123Pan async API client."""

from aio123pan.client import Pan123Client
from aio123pan.exceptions import (
    APIError,
    AuthenticationError,
    DownloadError,
    NetworkError,
    Pan123Error,
    RateLimitError,
    UploadError,
    ValidationError,
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
    "RateLimitError",
    "ValidationError",
    "NetworkError",
    "UploadError",
    "DownloadError",
    "__version__",
    "__version_tuple__",
]
