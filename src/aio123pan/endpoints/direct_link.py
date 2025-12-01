"""Direct link endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aio123pan.models.direct_link import (
    DirectLinkUrlResponse,
    DisableDirectLinkResponse,
    EnableDirectLinkResponse,
    IpBlacklistConfig,
    IpBlacklistSwitchResponse,
    OfflineLogResponse,
    TrafficLogResponse,
)

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class DirectLinkEndpoint:
    """Direct link related endpoints."""

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def get_offline_logs(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> OfflineLogResponse:
        """Get offline logs for direct links.

        Note: This API may return 404 and require special account permissions.

        Args:
            page: Page number (1-based)
            page_size: Number of logs per page

        Returns:
            OfflineLogResponse containing offline logs

        Raises:
            ResourceNotFoundError: If API endpoint is not available
        """
        params: dict[str, int] = {
            "page": page,
            "pageSize": page_size,
        }

        data = await self.client.get("/api/v1/directlink/offline/logs", params=params)
        return OfflineLogResponse.model_validate(data)

    async def get_traffic_logs(
        self,
        start_date: str,
        end_date: str,
        page: int = 1,
        page_size: int = 10,
    ) -> TrafficLogResponse:
        """Get traffic logs for direct links.

        Note: This API may return 404 and require special account permissions.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            page: Page number (1-based)
            page_size: Number of logs per page

        Returns:
            TrafficLogResponse containing traffic logs

        Raises:
            ResourceNotFoundError: If API endpoint is not available
        """
        params: dict[str, int | str] = {
            "startDate": start_date,
            "endDate": end_date,
            "page": page,
            "pageSize": page_size,
        }

        data = await self.client.get("/api/v1/directlink/traffic/logs", params=params)
        return TrafficLogResponse.model_validate(data)

    async def enable_direct_link(self, file_id: int) -> str:
        """Enable direct link space for a folder.

        Args:
            file_id: File ID of the folder to enable direct link for

        Returns:
            Filename of the enabled folder
        """
        payload: dict[str, int] = {"fileID": file_id}

        data = await self.client.post("/api/v1/direct-link/enable", json=payload)
        response = EnableDirectLinkResponse.model_validate(data)
        return response.filename

    async def get_direct_link_url(self, file_id: int) -> str:
        """Get direct link URL for a file.

        Args:
            file_id: File ID to get direct link URL for

        Returns:
            Direct link URL for the file
        """
        data = await self.client.get("/api/v1/direct-link/url", params={"fileID": file_id})
        response = DirectLinkUrlResponse.model_validate(data)
        return response.url

    async def disable_direct_link(self, file_id: int) -> str:
        """Disable direct link space for a folder.

        Args:
            file_id: File ID of the folder to disable direct link for

        Returns:
            Filename of the disabled folder
        """
        payload: dict[str, int] = {"fileID": file_id}

        data = await self.client.post("/api/v1/direct-link/disable", json=payload)
        response = DisableDirectLinkResponse.model_validate(data)
        return response.filename

    async def refresh_direct_link_cache(self) -> None:
        """Refresh direct link cache.

        This operation has no return value.
        """
        await self.client.post("/api/v1/direct-link/cache/refresh", json={})

    async def toggle_ip_blacklist(self, enable: bool) -> bool:
        """Toggle IP blacklist for direct links.

        Note: This API requires developer privileges.

        Args:
            enable: True to enable blacklist, False to disable

        Returns:
            True if operation succeeded
        """
        status = 1 if enable else 2
        payload: dict[str, int] = {"Status": status}

        data = await self.client.post("/api/v1/developer/config/forbide-ip/switch", json=payload)
        response = IpBlacklistSwitchResponse.model_validate(data)
        return response.done

    async def update_ip_blacklist(self, ip_list: list[str]) -> None:
        """Update IP blacklist for direct links.

        Note: This API requires developer privileges.

        Args:
            ip_list: List of IPv4 addresses to block (max 2000)

        Raises:
            ValidationError: If ip_list exceeds 2000 addresses
        """
        if len(ip_list) > 2000:
            from aio123pan.exceptions import ValidationError

            raise ValidationError("IP list cannot exceed 2000 addresses")

        payload: dict[str, list[str]] = {"IpList": ip_list}
        await self.client.post("/api/v1/developer/config/forbide-ip/update", json=payload)

    async def get_ip_blacklist(self) -> IpBlacklistConfig:
        """Get IP blacklist configuration for direct links.

        Note: This API requires developer privileges.

        Returns:
            IpBlacklistConfig containing IP list and status
        """
        data = await self.client.get("/api/v1/developer/config/forbide-ip/list")
        return IpBlacklistConfig.model_validate(data)
