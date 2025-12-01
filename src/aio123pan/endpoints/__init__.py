"""API endpoints for 123Pan."""

from aio123pan.endpoints.auth import AuthEndpoint
from aio123pan.endpoints.file import FileEndpoint
from aio123pan.endpoints.folder import FolderEndpoint
from aio123pan.endpoints.trash import TrashEndpoint
from aio123pan.endpoints.upload import UploadEndpoint
from aio123pan.endpoints.user import UserEndpoint

__all__ = [
    "AuthEndpoint",
    "UserEndpoint",
    "FileEndpoint",
    "FolderEndpoint",
    "UploadEndpoint",
    "TrashEndpoint",
]
