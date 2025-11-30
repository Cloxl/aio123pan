"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_client_id():
    """Mock client ID for testing."""
    return "test_client_id_123"


@pytest.fixture
def mock_client_secret():
    """Mock client secret for testing."""
    return "test_client_secret_456"


@pytest.fixture
def mock_access_token():
    """Mock access token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token"


@pytest.fixture
def mock_file_data():
    """Mock file data for testing."""
    return {
        "fileId": 123456,
        "filename": "test_file.txt",
        "type": 0,
        "size": 1024,
        "etag": "abc123def456",
        "status": 1,
        "parentFileId": 0,
        "category": 0,
        "trashed": 0,
    }


@pytest.fixture
def mock_folder_data():
    """Mock folder data for testing."""
    return {
        "fileId": 789012,
        "filename": "test_folder",
        "type": 1,
        "size": 0,
        "etag": "",
        "status": 1,
        "parentFileId": 0,
        "category": 0,
        "trashed": 0,
    }


@pytest.fixture
def mock_user_data():
    """Mock user data for testing."""
    return {
        "uid": 999999,
        "nickname": "TestUser",
        "spaceUse": 1024 * 1024 * 100,
        "spaceCapacity": 1024 * 1024 * 1024 * 10,
    }


@pytest.fixture
def mock_token_response():
    """Mock token response data."""
    return {"accessToken": "test_token_value", "expiredAt": "2025-12-31T23:59:59+08:00"}


@pytest.fixture
def mock_create_file_response_rapid():
    """Mock create file response for rapid upload."""
    return {"reuse": True, "fileID": 12345}


@pytest.fixture
def mock_create_file_response_normal():
    """Mock create file response for normal upload."""
    return {
        "reuse": False,
        "preuploadID": "upload_abc123",
        "sliceSize": 4194304,
        "servers": ["https://upload1.123pan.com"],
    }


@pytest.fixture
def temp_test_file(tmp_path):
    """Create a temporary test file."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content for upload")
    return file_path


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("PAN123_CLIENT_ID=test_id\nPAN123_CLIENT_SECRET=test_secret\n")
    return env_file


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "smoke: smoke tests for basic functionality")
    config.addinivalue_line("markers", "unit: unit tests for individual components")
    config.addinivalue_line("markers", "integration: integration tests requiring API access")
