"""Data models for share operations."""

from pydantic import BaseModel, ConfigDict, Field


class ShareInfo(BaseModel):
    """Share link information."""

    model_config = ConfigDict(populate_by_name=True)

    share_id: int = Field(alias="shareId")
    share_key: str = Field(alias="shareKey")
    share_name: str = Field(alias="shareName")
    expiration: str
    expired: int
    share_pwd: str = Field(alias="sharePwd", default="")
    traffic_switch: int = Field(alias="trafficSwitch", default=1)
    traffic_limit_switch: int = Field(alias="trafficLimitSwitch", default=1)
    traffic_limit: int = Field(alias="trafficLimit", default=0)
    bytes_charge: int = Field(alias="bytesCharge", default=0)
    preview_count: int = Field(alias="previewCount", default=0)
    download_count: int = Field(alias="downloadCount", default=0)
    save_count: int = Field(alias="saveCount", default=0)

    @property
    def share_url(self) -> str:
        """Get full share URL."""
        return f"https://www.123pan.com/s/{self.share_key}"

    @property
    def is_expired(self) -> bool:
        """Check if share link has expired."""
        return self.expired == 1

    @property
    def has_password(self) -> bool:
        """Check if share link has password protection."""
        return bool(self.share_pwd)


class ShareListResponse(BaseModel):
    """Response model for share list."""

    model_config = ConfigDict(populate_by_name=True)

    last_share_id: int = Field(alias="lastShareId")
    share_list: list[ShareInfo] = Field(alias="shareList", default_factory=list)

    @property
    def has_more(self) -> bool:
        """Check if there are more shares to fetch."""
        return self.last_share_id != -1


class CreateShareResponse(BaseModel):
    """Response model for create share."""

    model_config = ConfigDict(populate_by_name=True)

    share_id: int = Field(alias="shareID")
    share_key: str = Field(alias="shareKey")

    @property
    def share_url(self) -> str:
        """Get full share URL."""
        return f"https://www.123pan.com/s/{self.share_key}"
