"""Tests for exception handling."""

from unittest.mock import AsyncMock, patch

import pytest

from aio123pan import Pan123Client
from aio123pan.exceptions import (
    APIError,
    AuthenticationError,
    InvalidSharePeriodError,
    NetworkError,
    Pan123Error,
    RateLimitError,
    ResourceNotFoundError,
    ShareLimitExceededError,
    UnsupportedImageFormatError,
    ValidationError,
)

pytestmark = pytest.mark.unit


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_base_exception(self):
        """Test Pan123Error base exception."""
        error = Pan123Error("Test error", code=400, trace_id="trace_123")
        assert str(error) == "Test error (code: 400) [trace_id: trace_123]"
        assert error.message == "Test error"
        assert error.code == 400
        assert error.trace_id == "trace_123"

    def test_api_error(self):
        """Test APIError inherits from Pan123Error."""
        error = APIError("API error", code=500)
        assert isinstance(error, Pan123Error)
        assert error.message == "API error"

    def test_authentication_error(self):
        """Test AuthenticationError inherits from Pan123Error."""
        error = AuthenticationError("Auth failed")
        assert isinstance(error, Pan123Error)

    def test_rate_limit_error(self):
        """Test RateLimitError inherits from Pan123Error."""
        error = RateLimitError("Too many requests")
        assert isinstance(error, Pan123Error)

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError inherits from Pan123Error."""
        error = ResourceNotFoundError("Resource not found", code=404)
        assert isinstance(error, Pan123Error)

    def test_validation_error(self):
        """Test ValidationError inherits from Pan123Error."""
        error = ValidationError("Validation failed")
        assert isinstance(error, Pan123Error)

    def test_network_error(self):
        """Test NetworkError inherits from Pan123Error."""
        error = NetworkError("Network error")
        assert isinstance(error, Pan123Error)


class TestClientErrorHandling:
    """Test client error handling."""

    @pytest.mark.asyncio
    async def test_authentication_error_handling(self):
        """Test authentication error is raised."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = AuthenticationError("Unauthorized", code=401)

            async with client:
                with pytest.raises(AuthenticationError):
                    await client.user.get_user_info()

    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self):
        """Test rate limit error is raised."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = RateLimitError("Too Many Requests", code=429)

            async with client:
                with pytest.raises(RateLimitError):
                    await client.user.get_user_info()

    @pytest.mark.asyncio
    async def test_resource_not_found_error_handling(self):
        """Test resource not found error is raised."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = ResourceNotFoundError("Not Found", code=404)

            async with client:
                with pytest.raises(ResourceNotFoundError):
                    await client.user.get_user_info()


class TestValidationErrors:
    """Test validation error handling."""

    def test_invalid_filename(self):
        """Test invalid filename raises ValidationError."""
        from aio123pan.validators import validate_filename

        with pytest.raises(ValidationError, match="cannot contain"):
            validate_filename("invalid/filename.txt")

    def test_filename_too_long(self):
        """Test filename too long raises ValidationError."""
        from aio123pan.validators import validate_filename

        long_name = "a" * 256
        with pytest.raises(ValidationError, match="must be less than"):
            validate_filename(long_name)

    def test_invalid_batch_size(self):
        """Test invalid batch size raises ValidationError."""
        from aio123pan.validators import validate_batch_size

        with pytest.raises(ValidationError):
            validate_batch_size(0)

        with pytest.raises(ValidationError):
            validate_batch_size(101)

    def test_invalid_page_limit(self):
        """Test invalid page limit raises ValidationError."""
        from aio123pan.validators import validate_page_limit

        with pytest.raises(ValidationError):
            validate_page_limit(0)

        with pytest.raises(ValidationError):
            validate_page_limit(101)


class TestShareErrors:
    """Test share-specific errors."""

    def test_invalid_share_period(self):
        """Test invalid share period raises error."""
        error = InvalidSharePeriodError("Invalid expire_days: 5")
        assert isinstance(error, Pan123Error)
        assert "expire_days" in error.message

    def test_share_limit_exceeded(self):
        """Test share limit exceeded raises error."""
        error = ShareLimitExceededError("Too many files")
        assert isinstance(error, Pan123Error)

    @pytest.mark.asyncio
    async def test_create_share_invalid_expire_days(self):
        """Test creating share with invalid expire_days."""
        client = Pan123Client(client_id="test", client_secret="test")

        async with client:
            with pytest.raises(InvalidSharePeriodError):
                await client.share.create_share(
                    file_ids=[123456],
                    share_name="Test",
                    expire_days=5,  # Invalid: must be 0, 1, 7, or 30
                )


class TestImageErrors:
    """Test image-specific errors."""

    def test_unsupported_image_format(self):
        """Test unsupported image format raises error."""
        error = UnsupportedImageFormatError("Unsupported format: bmp")
        assert isinstance(error, Pan123Error)
        assert "bmp" in error.message


class TestNetworkErrors:
    """Test network-related errors."""

    @pytest.mark.asyncio
    async def test_network_error_on_connection_failure(self):
        """Test network error is raised on connection failure."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = NetworkError("Connection failed")

            async with client:
                with pytest.raises(NetworkError):
                    await client.user.get_user_info()


class TestErrorMessages:
    """Test error message formatting."""

    def test_error_with_trace_id(self):
        """Test error message includes trace_id."""
        error = APIError("Test error", code=500, trace_id="abc123")
        assert "abc123" in str(error)
        assert "500" in str(error)

    def test_error_without_trace_id(self):
        """Test error message without trace_id."""
        error = APIError("Test error", code=500)
        assert "Test error" in str(error)
        assert "500" in str(error)

    def test_error_without_code(self):
        """Test error message without code."""
        error = ValidationError("Validation failed")
        assert "Validation failed" in str(error)
