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


class AuthenticationError(Pan123Error):
    """Authentication failed (code = 401)."""


class RateLimitError(Pan123Error):
    """Rate limit exceeded (code = 429)."""


class NetworkError(Pan123Error):
    """Network-related errors."""


class ValidationError(Pan123Error):
    """Request validation error."""


class UploadError(Pan123Error):
    """Upload operation error."""


class DownloadError(Pan123Error):
    """Download operation error."""
