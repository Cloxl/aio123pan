"""Smoke tests for Pan123Client."""

import pytest

from aio123pan import Pan123Client, ValidationError
from aio123pan.config import get_settings
from aio123pan.storage import TokenStorage


class TestClientImport:
    """Test that client can be imported and instantiated."""

    def test_import_client(self):
        """Test importing Pan123Client."""
        from aio123pan import Pan123Client

        assert Pan123Client is not None

    def test_instantiate_client(self):
        """Test creating client instance."""
        client = Pan123Client(client_id="test_id", client_secret="test_secret")
        assert client is not None
        assert client.client_id == "test_id"
        assert client.client_secret == "test_secret"

    def test_client_without_credentials(self):
        """Test creating client without credentials."""
        client = Pan123Client()
        assert client is not None


class TestClientConfiguration:
    """Test client configuration and settings."""

    def test_explicit_credentials(self):
        """Test explicit credential override."""
        client = Pan123Client(client_id="explicit_id", client_secret="explicit_secret")
        assert client.client_id == "explicit_id"
        assert client.client_secret == "explicit_secret"

    def test_timeout_configuration(self):
        """Test timeout configuration."""
        client = Pan123Client(timeout=60.0)
        assert client._timeout == 60.0

    def test_base_url_configuration(self):
        """Test base URL configuration."""
        custom_url = "https://custom-api.example.com"
        client = Pan123Client(base_url=custom_url)
        assert client._base_url == custom_url

    def test_disable_token_storage(self):
        """Test disabling token storage."""
        client = Pan123Client(enable_token_storage=False)
        assert client._token_storage is None

    def test_token_storage_from_env(self, monkeypatch):
        """Test token storage configuration from environment variable."""
        monkeypatch.setenv("PAN123_ENABLE_TOKEN_STORAGE", "false")
        client = Pan123Client()
        assert client._token_storage is None

        monkeypatch.setenv("PAN123_ENABLE_TOKEN_STORAGE", "true")
        client = Pan123Client()
        assert client._token_storage is not None


class TestClientEndpoints:
    """Test client endpoint properties."""

    def test_auth_endpoint(self):
        """Test auth endpoint property."""
        client = Pan123Client()
        assert client.auth is not None
        assert client.auth is client.auth

    def test_user_endpoint(self):
        """Test user endpoint property."""
        client = Pan123Client()
        assert client.user is not None
        assert client.user is client.user

    def test_file_endpoint(self):
        """Test file endpoint property."""
        client = Pan123Client()
        assert client.file is not None
        assert client.file is client.file

    def test_folder_endpoint(self):
        """Test folder endpoint property."""
        client = Pan123Client()
        assert client.folder is not None
        assert client.folder is client.folder

    def test_upload_endpoint(self):
        """Test upload endpoint property."""
        client = Pan123Client()
        assert client.upload is not None
        assert client.upload is client.upload

    def test_trash_endpoint(self):
        """Test trash endpoint property."""
        client = Pan123Client()
        assert client.trash is not None
        assert client.trash is client.trash


class TestExceptionHandling:
    """Test exception imports and inheritance."""

    def test_import_exceptions(self):
        """Test importing exceptions."""
        from aio123pan import APIError, AuthenticationError, Pan123Error, RateLimitError, ValidationError

        assert Pan123Error is not None
        assert APIError is not None
        assert AuthenticationError is not None
        assert RateLimitError is not None
        assert ValidationError is not None

    def test_exception_hierarchy(self):
        """Test exception inheritance."""
        from aio123pan import APIError, AuthenticationError, Pan123Error, RateLimitError

        assert issubclass(APIError, Pan123Error)
        assert issubclass(AuthenticationError, Pan123Error)
        assert issubclass(RateLimitError, Pan123Error)

    def test_exception_instantiation(self):
        """Test creating exception instances."""
        from aio123pan import Pan123Error

        error = Pan123Error("Test error", code=400, trace_id="trace_123")
        assert str(error) == "Test error (code: 400) [trace_id: trace_123]"


class TestConfigurationLoading:
    """Test configuration loading from settings."""

    def test_get_settings(self):
        """Test getting settings."""
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, "client_id")
        assert hasattr(settings, "client_secret")
        assert hasattr(settings, "timeout")
        assert hasattr(settings, "base_url")

    def test_default_timeout(self):
        """Test default timeout value."""
        settings = get_settings()
        assert settings.timeout == 30.0

    def test_default_base_url(self):
        """Test default base URL."""
        settings = get_settings()
        assert settings.base_url == "https://open-api.123pan.com"


class TestTokenStorage:
    """Test token storage functionality."""

    def test_token_storage_init(self):
        """Test token storage initialization."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            storage = TokenStorage(env_file)
            assert storage.env_file == env_file

    def test_token_storage_keys(self):
        """Test token storage key constants."""
        assert TokenStorage.TOKEN_KEY == "AIO123PAN_CACHED_ACCESS_TOKEN"
        assert TokenStorage.EXPIRY_KEY == "AIO123PAN_CACHED_TOKEN_EXPIRY"


class TestModuleVersion:
    """Test module version information."""

    def test_version_attribute(self):
        """Test __version__ attribute exists."""
        from aio123pan import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_version_tuple_attribute(self):
        """Test __version_tuple__ attribute exists."""
        from aio123pan import __version_tuple__

        assert __version_tuple__ is not None
        assert isinstance(__version_tuple__, tuple)


class TestModuleExports:
    """Test module __all__ exports."""

    def test_all_exports(self):
        """Test __all__ contains expected exports."""
        from aio123pan import __all__

        expected_exports = [
            "Pan123Client",
            "Pan123Error",
            "APIError",
            "AuthenticationError",
            "RateLimitError",
            "ValidationError",
            "__version__",
            "__version_tuple__",
        ]

        for export in expected_exports:
            assert export in __all__


class TestClientContextManager:
    """Test client context manager protocol."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test client works as async context manager."""
        client = Pan123Client(client_id="test", client_secret="test")
        async with client:
            assert client._client is not None

    @pytest.mark.asyncio
    async def test_client_cleanup(self):
        """Test client cleanup after context exit."""
        client = Pan123Client(client_id="test", client_secret="test")
        async with client:
            pass
        assert client._client is None


class TestUtilityFunctions:
    """Test utility functions."""

    def test_calculate_md5_import(self):
        """Test MD5 calculation function can be imported."""
        from aio123pan.utils import calculate_md5, calculate_md5_from_bytes

        assert calculate_md5 is not None
        assert calculate_md5_from_bytes is not None

    def test_calculate_md5_from_bytes(self):
        """Test MD5 calculation from bytes."""
        from aio123pan.utils import calculate_md5_from_bytes

        data = b"test data"
        md5_hash = calculate_md5_from_bytes(data)
        assert isinstance(md5_hash, str)
        assert len(md5_hash) == 32


class TestConstants:
    """Test module constants."""

    def test_constants_import(self):
        """Test importing constants."""
        from aio123pan.constants import BASE_URL, CONTENT_TYPE, DEFAULT_TIMEOUT, PLATFORM

        assert BASE_URL == "https://open-api.123pan.com"
        assert PLATFORM == "open_platform"
        assert CONTENT_TYPE == "application/json"
        assert DEFAULT_TIMEOUT == 30.0


class TestValidationIntegration:
    """Test validation integration with endpoints."""

    def test_filename_validation_in_upload(self):
        """Test filename validation is applied."""
        from aio123pan.validators import validate_filename

        with pytest.raises(ValidationError):
            validate_filename("invalid/filename.txt")

    def test_batch_size_validation(self):
        """Test batch size validation."""
        from aio123pan.validators import validate_batch_size

        validate_batch_size(50)

        with pytest.raises(ValidationError):
            validate_batch_size(101)

    def test_page_limit_validation(self):
        """Test page limit validation."""
        from aio123pan.validators import validate_page_limit

        validate_page_limit(50)

        with pytest.raises(ValidationError):
            validate_page_limit(101)
