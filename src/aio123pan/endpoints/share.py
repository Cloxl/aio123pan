"""Share management endpoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from aio123pan.exceptions import InvalidSharePeriodError, ShareLimitExceededError
from aio123pan.models.share import CreateShareResponse, ShareInfo, ShareListResponse

if TYPE_CHECKING:
    from aio123pan.client import Pan123Client


class ShareEndpoint:
    """Share management related endpoints."""

    VALID_EXPIRE_DAYS = {0, 1, 7, 30}

    def __init__(self, client: Pan123Client) -> None:
        self.client = client

    async def create_share(
        self,
        file_ids: list[int],
        share_name: str,
        expire_days: int,
        share_pwd: str | None = None,
        traffic_switch: int | None = None,
        traffic_limit_switch: int | None = None,
        traffic_limit: int | None = None,
    ) -> CreateShareResponse:
        """Create a share link.

        Args:
            file_ids: List of file IDs to share (max 100)
            share_name: Share link name
            expire_days: Expiration days (must be 1, 7, 30, or 0 for permanent)
            share_pwd: Optional password for share link
            traffic_switch: Traffic package switch (1=all off, 2=guest, 3=over-quota, 4=all on)
            traffic_limit_switch: Traffic limit switch (1=off, 2=on)
            traffic_limit: Traffic limit in bytes

        Returns:
            CreateShareResponse containing share_id and share_key
        """
        if expire_days not in self.VALID_EXPIRE_DAYS:
            raise InvalidSharePeriodError(
                f"expire_days must be one of {self.VALID_EXPIRE_DAYS}, got {expire_days}",
            )

        if len(file_ids) > 100:
            raise ShareLimitExceededError(f"Cannot share more than 100 files, got {len(file_ids)}")

        payload: dict[str, str | int] = {
            "shareName": share_name,
            "shareExpire": expire_days,
            "fileIDList": ",".join(str(fid) for fid in file_ids),
        }

        if share_pwd is not None:
            payload["sharePwd"] = share_pwd
        if traffic_switch is not None:
            payload["trafficSwitch"] = traffic_switch
        if traffic_limit_switch is not None:
            payload["trafficLimitSwitch"] = traffic_limit_switch
        if traffic_limit is not None:
            payload["trafficLimit"] = traffic_limit

        data = await self.client.post("/api/v1/share/create", json=payload)
        return CreateShareResponse.model_validate(data)

    async def list_shares(
        self,
        limit: int = 100,
        last_share_id: int | None = None,
    ) -> ShareListResponse:
        """List share links.

        Args:
            limit: Number of shares per page (max 100)
            last_share_id: Pagination parameter from previous response

        Returns:
            ShareListResponse containing share list and pagination info
        """
        from aio123pan.validators import validate_page_limit

        validate_page_limit(limit)

        params: dict[str, int] = {"limit": limit}
        if last_share_id is not None:
            params["lastShareId"] = last_share_id

        data = await self.client.get("/api/v1/share/list", params=params)
        return ShareListResponse.model_validate(data)

    async def list_all_shares(self, limit: int = 100) -> AsyncIterator[ShareInfo]:
        """List all shares with automatic pagination.

        Args:
            limit: Number of shares per page (max 100)

        Yields:
            ShareInfo objects
        """
        last_share_id = None
        while True:
            response = await self.list_shares(limit=limit, last_share_id=last_share_id)

            for share_info in response.share_list:
                yield share_info

            if not response.has_more:
                break

            last_share_id = response.last_share_id

    async def update_share(
        self,
        share_id: int,
        share_name: str | None = None,
        expire_days: int | None = None,
        share_pwd: str | None = None,
        traffic_switch: int | None = None,
        traffic_limit_switch: int | None = None,
        traffic_limit: int | None = None,
    ) -> bool:
        """Update a share link.

        Note: This API may return 404 and require special account permissions.

        Args:
            share_id: Share ID to update
            share_name: New share link name
            expire_days: New expiration days (must be 1, 7, 30, or 0 for permanent)
            share_pwd: New password for share link
            traffic_switch: Traffic package switch (1=all off, 2=guest, 3=over-quota, 4=all on)
            traffic_limit_switch: Traffic limit switch (1=off, 2=on)
            traffic_limit: Traffic limit in bytes

        Returns:
            True if update was successful

        Raises:
            ResourceNotFoundError: If API endpoint is not available
        """
        if expire_days is not None and expire_days not in self.VALID_EXPIRE_DAYS:
            raise InvalidSharePeriodError(
                f"expire_days must be one of {self.VALID_EXPIRE_DAYS}, got {expire_days}",
            )

        payload: dict[str, str | int] = {"shareId": share_id}

        if share_name is not None:
            payload["shareName"] = share_name
        if expire_days is not None:
            payload["shareExpire"] = expire_days
        if share_pwd is not None:
            payload["sharePwd"] = share_pwd
        if traffic_switch is not None:
            payload["trafficSwitch"] = traffic_switch
        if traffic_limit_switch is not None:
            payload["trafficLimitSwitch"] = traffic_limit_switch
        if traffic_limit is not None:
            payload["trafficLimit"] = traffic_limit

        await self.client.put("/api/v1/share/update", json=payload)
        return True

    async def create_paid_share(
        self,
        file_ids: list[int],
        share_name: str,
        expire_days: int,
        price: int,
        share_pwd: str | None = None,
    ) -> CreateShareResponse:
        """Create a paid share link.

        Note: This API may return 404 and require special account permissions or features.

        Args:
            file_ids: List of file IDs to share (max 100)
            share_name: Share link name
            expire_days: Expiration days (must be 1, 7, 30, or 0 for permanent)
            price: Price in cents (minimum unit)
            share_pwd: Optional password for share link

        Returns:
            CreateShareResponse containing share_id and share_key

        Raises:
            ResourceNotFoundError: If API endpoint is not available
            InvalidSharePeriodError: If expire_days is invalid
        """
        if expire_days not in self.VALID_EXPIRE_DAYS:
            raise InvalidSharePeriodError(
                f"expire_days must be one of {self.VALID_EXPIRE_DAYS}, got {expire_days}",
            )

        if len(file_ids) > 100:
            raise ShareLimitExceededError(f"Cannot share more than 100 files, got {len(file_ids)}")

        payload: dict[str, str | int] = {
            "shareName": share_name,
            "shareExpire": expire_days,
            "fileIDList": ",".join(str(fid) for fid in file_ids),
            "price": price,
        }

        if share_pwd is not None:
            payload["sharePwd"] = share_pwd

        data = await self.client.post("/api/v1/share/paid/create", json=payload)
        return CreateShareResponse.model_validate(data)

    async def list_paid_shares(
        self,
        limit: int = 100,
        last_share_id: int | None = None,
    ) -> ShareListResponse:
        """List paid share links.

        Note: This API may return 404 and require special account permissions or features.

        Args:
            limit: Number of shares per page (max 100)
            last_share_id: Pagination parameter from previous response

        Returns:
            ShareListResponse containing share list and pagination info

        Raises:
            ResourceNotFoundError: If API endpoint is not available
        """
        from aio123pan.validators import validate_page_limit

        validate_page_limit(limit)

        params: dict[str, int] = {"limit": limit}
        if last_share_id is not None:
            params["lastShareId"] = last_share_id

        data = await self.client.get("/api/v1/share/paid/list", params=params)
        return ShareListResponse.model_validate(data)

    async def update_paid_share(
        self,
        share_id: int,
        share_name: str | None = None,
        expire_days: int | None = None,
        price: int | None = None,
        share_pwd: str | None = None,
    ) -> bool:
        """Update a paid share link.

        Note: This API may return 404 and require special account permissions or features.

        Args:
            share_id: Share ID to update
            share_name: New share link name
            expire_days: New expiration days (must be 1, 7, 30, or 0 for permanent)
            price: New price in cents
            share_pwd: New password for share link

        Returns:
            True if update was successful

        Raises:
            ResourceNotFoundError: If API endpoint is not available
            InvalidSharePeriodError: If expire_days is invalid
        """
        if expire_days is not None and expire_days not in self.VALID_EXPIRE_DAYS:
            raise InvalidSharePeriodError(
                f"expire_days must be one of {self.VALID_EXPIRE_DAYS}, got {expire_days}",
            )

        payload: dict[str, str | int] = {"shareId": share_id}

        if share_name is not None:
            payload["shareName"] = share_name
        if expire_days is not None:
            payload["shareExpire"] = expire_days
        if price is not None:
            payload["price"] = price
        if share_pwd is not None:
            payload["sharePwd"] = share_pwd

        await self.client.put("/api/v1/share/paid/update", json=payload)
        return True
