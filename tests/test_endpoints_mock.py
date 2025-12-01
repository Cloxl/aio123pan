"""Mock tests for all endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from aio123pan import Pan123Client
from aio123pan.models.file import FileInfo, FileListResponse
from aio123pan.models.share import ShareInfo, ShareListResponse, CreateShareResponse
from aio123pan.models.direct_link import (
    EnableDirectLinkResponse,
    DisableDirectLinkResponse,
    DirectLinkUrlResponse,
    IpBlacklistConfig,
)
from aio123pan.models.offline import OfflineTaskInfo
from aio123pan.models.image import ImageInfo
from aio123pan.models.video import TranscodeTaskInfo


pytestmark = pytest.mark.mock


class TestFileEndpointMock:
    """Mock tests for file endpoint."""

    @pytest.mark.asyncio
    async def test_list_files(self, mock_file_data, mock_folder_data):
        """Test listing files with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {
            "lastFileId": -1,
            "fileList": [mock_file_data, mock_folder_data],
        }

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.file.list_files(parent_file_id=0)

                assert isinstance(result, FileListResponse)
                assert len(result.file_list) == 2
                assert result.file_list[0].filename == "test_file.txt"
                assert result.file_list[1].filename == "test_folder"
                assert result.file_list[0].is_file
                assert result.file_list[1].is_folder

    @pytest.mark.asyncio
    async def test_delete_file(self):
        """Test deleting a file with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}
            async with client:
                result = await client.file.delete_file(123456)

                assert result is True
                mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_file(self):
        """Test moving a file with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}
            async with client:
                result = await client.file.move_file(123456, 789)

                assert result is True

    @pytest.mark.asyncio
    async def test_rename_file(self):
        """Test renaming a file with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}
            async with client:
                result = await client.file.rename_file(123456, "new_name.txt")

                assert result is True


class TestShareEndpointMock:
    """Mock tests for share endpoint."""

    @pytest.mark.asyncio
    async def test_create_share(self):
        """Test creating a share with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {
            "shareID": 111222,
            "shareKey": "abc123",
        }

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.share.create_share(
                    file_ids=[123456],
                    share_name="Test Share",
                    expire_days=7,
                    share_pwd="1234",
                )

                assert isinstance(result, CreateShareResponse)
                assert result.share_id == 111222
                assert result.share_url == "https://www.123pan.com/s/abc123"

    @pytest.mark.asyncio
    async def test_list_shares(self, mock_share_list_response):
        """Test listing shares with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_share_list_response
            async with client:
                result = await client.share.list_shares(limit=10)

                assert isinstance(result, ShareListResponse)
                assert len(result.share_list) == 2
                assert result.share_list[0].share_name == "Share 1"
                assert result.share_list[0].has_password
                assert not result.share_list[1].has_password


class TestDirectLinkEndpointMock:
    """Mock tests for direct link endpoint."""

    @pytest.mark.asyncio
    async def test_enable_direct_link(self):
        """Test enabling direct link with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {"filename": "test_folder"}

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.direct_link.enable_direct_link(123456)

                assert result == "test_folder"

    @pytest.mark.asyncio
    async def test_get_direct_link_url(self):
        """Test getting direct link URL with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {"url": "https://123pan.com/dl/abc123"}

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.direct_link.get_direct_link_url(123456)

                assert result == "https://123pan.com/dl/abc123"

    @pytest.mark.asyncio
    async def test_disable_direct_link(self):
        """Test disabling direct link with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {"filename": "test_folder"}

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.direct_link.disable_direct_link(123456)

                assert result == "test_folder"

    @pytest.mark.asyncio
    async def test_get_ip_blacklist(self, mock_ip_blacklist_data):
        """Test getting IP blacklist with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_ip_blacklist_data
            async with client:
                result = await client.direct_link.get_ip_blacklist()

                assert isinstance(result, IpBlacklistConfig)
                assert len(result.ip_list) == 2
                assert result.is_enabled


class TestOfflineEndpointMock:
    """Mock tests for offline download endpoint."""

    @pytest.mark.asyncio
    async def test_create_download_task(self):
        """Test creating offline download task with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {"taskID": 555666}

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.offline.create_download_task(
                    url="https://example.com/file.zip",
                    file_name="file.zip",
                )

                assert result == 555666

    @pytest.mark.asyncio
    async def test_get_download_progress(self, mock_offline_task_data):
        """Test getting download progress with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_offline_task_data
            async with client:
                result = await client.offline.get_download_progress(555666)

                assert isinstance(result, OfflineTaskInfo)
                assert result.task_id == 555666
                assert result.progress == 50
                assert result.is_in_progress


class TestImageEndpointMock:
    """Mock tests for image hosting endpoint."""

    @pytest.mark.asyncio
    async def test_copy_cloud_image(self):
        """Test copying cloud image with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {"directUrl": "https://img.123pan.com/abc123.png"}

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.image.copy_cloud_image(123456)

                assert result == "https://img.123pan.com/abc123.png"


class TestVideoEndpointMock:
    """Mock tests for video transcode endpoint."""

    @pytest.mark.asyncio
    async def test_create_transcode_task(self):
        """Test creating video transcode task with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {"taskID": 777888}

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.video.create_transcode_task(123456)

                assert result == 777888

    @pytest.mark.asyncio
    async def test_get_transcode_status(self, mock_video_task_data):
        """Test getting transcode status with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_video_task_data
            async with client:
                result = await client.video.get_transcode_status(777888)

                assert isinstance(result, TranscodeTaskInfo)
                assert result.task_id == 777888
                assert result.is_in_progress


class TestTrashEndpointMock:
    """Mock tests for trash endpoint."""

    @pytest.mark.asyncio
    async def test_list_trash(self, mock_trash_list_response):
        """Test listing trash with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_trash_list_response
            async with client:
                result = await client.trash.list_trash(limit=10)

                assert isinstance(result, FileListResponse)
                assert len(result.file_list) == 1
                assert result.file_list[0].filename == "deleted_file.txt"

    @pytest.mark.asyncio
    async def test_empty_trash(self):
        """Test emptying trash with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {}
            async with client:
                result = await client.trash.empty_trash()

                assert result is True


class TestFolderEndpointMock:
    """Mock tests for folder endpoint."""

    @pytest.mark.asyncio
    async def test_create_folder(self):
        """Test creating folder with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        mock_response = {"dirID": 789012}

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            async with client:
                result = await client.folder.create_folder(parent_file_id=0, name="test_folder")

                assert result == 789012


class TestUserEndpointMock:
    """Mock tests for user endpoint."""

    @pytest.mark.asyncio
    async def test_get_user_info(self, mock_user_data):
        """Test getting user info with mock data."""
        client = Pan123Client(client_id="test", client_secret="test")

        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_user_data
            async with client:
                result = await client.user.get_user_info()

                assert result.user_id == 999999
                assert result.nickname == "TestUser"
                assert result.space_used > 0
