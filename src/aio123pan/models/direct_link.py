"""Data models for direct link operations."""

from pydantic import BaseModel, ConfigDict, Field


class OfflineLog(BaseModel):
    """Offline log entry for direct links."""

    model_config = ConfigDict(populate_by_name=True)

    log_id: int = Field(alias="logID")
    timestamp: str
    ip_address: str = Field(alias="ipAddress")
    action: str


class OfflineLogResponse(BaseModel):
    """Response model for offline logs."""

    model_config = ConfigDict(populate_by_name=True)

    logs: list[OfflineLog] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(alias="pageSize", default=10)

    @property
    def has_more(self) -> bool:
        """Check if there are more logs to fetch."""
        return self.page * self.page_size < self.total


class TrafficLog(BaseModel):
    """Traffic log entry for direct links."""

    model_config = ConfigDict(populate_by_name=True)

    date: str
    traffic_used: int = Field(alias="trafficUsed")
    request_count: int = Field(alias="requestCount")

    @property
    def traffic_mb(self) -> float:
        """Get traffic used in MB."""
        return self.traffic_used / (1024 * 1024)

    @property
    def traffic_gb(self) -> float:
        """Get traffic used in GB."""
        return self.traffic_used / (1024 * 1024 * 1024)


class TrafficLogResponse(BaseModel):
    """Response model for traffic logs."""

    model_config = ConfigDict(populate_by_name=True)

    logs: list[TrafficLog] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(alias="pageSize", default=10)

    @property
    def has_more(self) -> bool:
        """Check if there are more logs to fetch."""
        return self.page * self.page_size < self.total

    @property
    def total_traffic_mb(self) -> float:
        """Get total traffic used in MB across all logs."""
        return sum(log.traffic_mb for log in self.logs)

    @property
    def total_traffic_gb(self) -> float:
        """Get total traffic used in GB across all logs."""
        return sum(log.traffic_gb for log in self.logs)

    @property
    def total_requests(self) -> int:
        """Get total request count across all logs."""
        return sum(log.request_count for log in self.logs)


class EnableDirectLinkResponse(BaseModel):
    """Response model for enabling direct link space."""

    model_config = ConfigDict(populate_by_name=True)

    filename: str


class DisableDirectLinkResponse(BaseModel):
    """Response model for disabling direct link space."""

    model_config = ConfigDict(populate_by_name=True)

    filename: str


class DirectLinkUrlResponse(BaseModel):
    """Response model for getting direct link URL."""

    model_config = ConfigDict(populate_by_name=True)

    url: str


class IpBlacklistConfig(BaseModel):
    """IP blacklist configuration."""

    model_config = ConfigDict(populate_by_name=True)

    ip_list: list[str] = Field(alias="ipList", default_factory=list)
    status: int

    @property
    def is_enabled(self) -> bool:
        """Check if blacklist is enabled (1=enabled, 2=disabled)."""
        return self.status == 1


class IpBlacklistSwitchResponse(BaseModel):
    """Response model for toggling IP blacklist."""

    model_config = ConfigDict(populate_by_name=True)

    done: bool = Field(alias="Done")
