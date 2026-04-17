"""Admin API schemas for SentinelGuard."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BlacklistCreate(BaseModel):
    """Schema for creating blacklist entries."""
    ip: str = Field(..., description="IP address to blacklist")
    reason: str = Field(..., description="Reason for blacklisting")
    permanent: bool = Field(default=False, description="Whether blacklist is permanent")
    duration_hours: Optional[int] = Field(
        default=None, 
        description="Duration in hours for temporary blacklist"
    )


class WhitelistCreate(BaseModel):
    """Schema for creating whitelist entries."""
    ip: str = Field(..., description="IP address to whitelist")
    reason: str = Field(..., description="Reason for whitelisting")
    permanent: bool = Field(default=False, description="Whether whitelist is permanent")
    duration_hours: Optional[int] = Field(
        default=None, 
        description="Duration in hours for temporary whitelist"
    )


class BaseIPListResponse(BaseModel):
    """Base schema for IP list responses."""
    id: int
    ip: str
    reason: str
    permanent: bool
    expires_at: Optional[datetime]
    created_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True


class BlacklistResponse(BaseIPListResponse):
    """Schema for blacklist responses."""
    pass


class WhitelistResponse(BaseIPListResponse):
    """Schema for whitelist responses."""
    pass


class AdminStatsResponse(BaseModel):
    """Schema for admin statistics."""
    blacklist: dict
    whitelist: dict
    recent_activity: dict
    timestamp: str


class CleanupResponse(BaseModel):
    """Schema for cleanup operation response."""
    message: str
    expired_blacklist_entries: int
    expired_whitelist_entries: int
