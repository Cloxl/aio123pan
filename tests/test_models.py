"""Tests for data models."""

from datetime import datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from aio123pan.models.auth import AccessTokenResponse
from aio123pan.models.file import FileInfo, FileListResponse
from aio123pan.models.upload import CreateFileResponse, UploadCompleteResponse, UploadDomainResponse
from aio123pan.models.user import UserInfo


class TestAccessTokenResponse:
    """Tests for AccessTokenResponse model."""

    def test_valid_token_response(self):
        """Test valid access token response."""
        data = {
            "accessToken": "test_token_123",
            "expiredAt": "2025-12-31T23:59:59+08:00",
        }
        response = AccessTokenResponse.model_validate(data)
        assert response.access_token == "test_token_123"
        assert isinstance(response.expired_at, datetime)

    def test_missing_required_fields(self):
        """Test missing required fields raises error."""
        with pytest.raises(PydanticValidationError):
            AccessTokenResponse.model_validate({})


class TestUserInfo:
    """Tests for UserInfo model."""

    def test_valid_user_info(self):
        """Test valid user info."""
        data = {
            "uid": 123456,
            "nickname": "TestUser",
            "spaceUse": 1024 * 1024 * 100,
            "spaceCapacity": 1024 * 1024 * 1024 * 10,
        }
        user = UserInfo.model_validate(data)
        assert user.user_id == 123456
        assert user.nickname == "TestUser"
        assert user.space_used == 1024 * 1024 * 100
        assert user.space_capacity == 1024 * 1024 * 1024 * 10


class TestFileInfo:
    """Tests for FileInfo model."""

    def test_valid_file_info(self):
        """Test valid file info."""
        data = {
            "fileId": 123,
            "filename": "test.txt",
            "type": 0,
            "size": 1024,
            "etag": "abc123",
            "status": 1,
            "parentFileId": 0,
            "category": 0,
            "trashed": False,
        }
        file_info = FileInfo.model_validate(data)
        assert file_info.file_id == 123
        assert file_info.filename == "test.txt"
        assert file_info.is_file
        assert not file_info.is_folder

    def test_folder_info(self):
        """Test folder type detection."""
        data = {
            "fileId": 456,
            "filename": "folder",
            "type": 1,
            "size": 0,
            "etag": "",
            "status": 1,
            "parentFileId": 0,
            "category": 0,
        }
        file_info = FileInfo.model_validate(data)
        assert file_info.is_folder
        assert not file_info.is_file

    def test_trashed_file(self):
        """Test trashed file detection."""
        data = {
            "fileId": 789,
            "filename": "deleted.txt",
            "type": 0,
            "size": 1024,
            "etag": "def456",
            "status": 1,
            "parentFileId": 0,
            "category": 0,
            "trashed": 1,
        }
        file_info = FileInfo.model_validate(data)
        assert file_info.trashed


class TestFileListResponse:
    """Tests for FileListResponse model."""

    def test_valid_file_list(self):
        """Test valid file list response."""
        data = {
            "lastFileId": 100,
            "fileList": [
                {
                    "fileId": 1,
                    "filename": "file1.txt",
                    "type": 0,
                    "size": 1024,
                    "etag": "abc",
                    "status": 1,
                    "parentFileId": 0,
                    "category": 0,
                },
            ],
        }
        response = FileListResponse.model_validate(data)
        assert response.last_file_id == 100
        assert len(response.file_list) == 1
        assert response.has_more

    def test_last_page(self):
        """Test detection of last page."""
        data = {"lastFileId": -1, "fileList": []}
        response = FileListResponse.model_validate(data)
        assert not response.has_more

    def test_empty_file_list(self):
        """Test empty file list."""
        data = {"lastFileId": -1, "fileList": []}
        response = FileListResponse.model_validate(data)
        assert len(response.file_list) == 0


class TestCreateFileResponse:
    """Tests for CreateFileResponse model."""

    def test_rapid_upload(self):
        """Test rapid upload response."""
        data = {
            "reuse": True,
            "fileID": 12345,
        }
        response = CreateFileResponse.model_validate(data)
        assert response.is_rapid_upload
        assert response.file_id == 12345

    def test_normal_upload(self):
        """Test normal upload response."""
        data = {
            "reuse": False,
            "preuploadID": "upload_123",
            "sliceSize": 4194304,
            "servers": ["https://upload1.123pan.com", "https://upload2.123pan.com"],
        }
        response = CreateFileResponse.model_validate(data)
        assert not response.is_rapid_upload
        assert response.preupload_id == "upload_123"
        assert response.slice_size == 4194304
        assert len(response.servers) == 2


class TestUploadCompleteResponse:
    """Tests for UploadCompleteResponse model."""

    def test_upload_completed(self):
        """Test completed upload."""
        data = {"completed": True, "fileID": 98765}
        response = UploadCompleteResponse.model_validate(data)
        assert response.completed
        assert response.file_id == 98765

    def test_upload_not_completed(self):
        """Test incomplete upload."""
        data = {"completed": False, "fileID": 0}
        response = UploadCompleteResponse.model_validate(data)
        assert not response.completed


class TestUploadDomainResponse:
    """Tests for UploadDomainResponse model."""

    def test_upload_domains(self):
        """Test upload domain response."""
        data = {"servers": ["https://upload1.123pan.com", "https://upload2.123pan.com"]}
        response = UploadDomainResponse.model_validate(data)
        assert len(response.servers) == 2

    def test_empty_servers(self):
        """Test empty servers list."""
        data = {"servers": []}
        response = UploadDomainResponse.model_validate(data)
        assert len(response.servers) == 0
