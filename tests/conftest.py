"""Pytest configuration and fixtures."""

from unittest.mock import AsyncMock, Mock

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
        "spaceUsed": 1024 * 1024 * 100,
        "spaceCapacity": 1024 * 1024 * 1024 * 10,
        "spacePermanent": 1024 * 1024 * 1024,
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
def mock_share_data():
    """Mock share data for testing."""
    return {
        "shareID": 111222,
        "shareName": "Test Share",
        "shareKey": "abc123",
        "sharePwd": "1234",
        "expiration": 1735660799,
        "expired": 0,
        "downloadCount": 10,
        "saveCount": 5,
        "previewCount": 20,
        "shareStatus": 1,
    }


@pytest.fixture
def mock_share_list_response():
    """Mock share list response."""
    return {
        "lastShareId": 111222,
        "shareList": [
            {
                "shareId": 111222,
                "shareName": "Share 1",
                "shareKey": "key1",
                "sharePwd": "1234",
                "expiration": "2025-12-31",
                "expired": 0,
                "downloadCount": 5,
                "saveCount": 2,
                "previewCount": 10,
                "trafficSwitch": 1,
                "trafficLimitSwitch": 1,
                "trafficLimit": 0,
                "bytesCharge": 0,
            },
            {
                "shareId": 111223,
                "shareName": "Share 2",
                "shareKey": "key2",
                "sharePwd": "",
                "expiration": "2025-06-30",
                "expired": 0,
                "downloadCount": 3,
                "saveCount": 1,
                "previewCount": 8,
                "trafficSwitch": 1,
                "trafficLimitSwitch": 1,
                "trafficLimit": 0,
                "bytesCharge": 0,
            },
        ],
    }


@pytest.fixture
def mock_direct_link_data():
    """Mock direct link data for testing."""
    return {"filename": "test_folder", "url": "https://123pan.com/dl/abc123"}


@pytest.fixture
def mock_offline_task_data():
    """Mock offline download task data."""
    return {"taskID": 555666, "status": 2, "progress": 50, "failReason": "", "fileID": 123456, "url": "https://example.com/file.zip"}


@pytest.fixture
def mock_image_data():
    """Mock image hosting data."""
    return {"fileID": 888999, "directUrl": "https://img.123pan.com/abc123.png", "size": 102400}


@pytest.fixture
def mock_video_task_data():
    """Mock video transcode task data."""
    return {"taskID": 777888, "fileID": 123456, "status": 1, "progress": 100}


@pytest.fixture
def mock_trash_list_response():
    """Mock trash list response."""
    return {
        "lastFileId": 123456,
        "fileList": [
            {
                "fileId": 123456,
                "filename": "deleted_file.txt",
                "type": 0,
                "size": 2048,
                "etag": "def456",
                "status": 1,
                "parentFileId": 0,
                "category": 0,
                "trashed": 1,
            }
        ],
    }


@pytest.fixture
def mock_ip_blacklist_data():
    """Mock IP blacklist configuration data."""
    return {"ipList": ["192.168.1.1", "10.0.0.1"], "status": 1}


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient."""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": 0, "message": "success", "data": {}}
    mock_client.request.return_value = mock_response
    return mock_client


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
    config.addinivalue_line("markers", "mock: tests using mocked API responses")

