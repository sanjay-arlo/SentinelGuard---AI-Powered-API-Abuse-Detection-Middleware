"""Blacklist model for blocked IP addresses."""

from sqlalchemy import Column, String, Boolean, Index, DateTime
from sqlalchemy.dialects.postgresql import INET

from ..base import BaseModel


class Blacklist(BaseModel):
    """Model for IP blacklist entries."""
    
    __tablename__ = "blacklist"
    
    ip_address = Column(
        INET,
        nullable=False,
        unique=True,
        comment="Blocked IP address"
    )
    
    reason = Column(
        String(500),
        nullable=False,
        comment="Reason for blocking"
    )
    
    blocked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default='NOW()',
        comment="When the IP was blocked"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the block expires (NULL = permanent)"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default='true',
        comment="Whether the block is currently active"
    )
    
    created_by = Column(
        String(100),
        nullable=False,
        default='system',
        server_default='system',
        comment="Who created the block (system or admin)"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blacklist_active', 'ip_address', postgresql_where='is_active = TRUE'),
        Index('idx_blacklist_expires', 'expires_at'),
        Index('idx_blacklist_created_at', 'blocked_at'),
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if block has expired."""
        if self.expires_at is None:
            return False
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_permanent(self) -> bool:
        """Check if block is permanent."""
        return self.expires_at is None
    
    def __repr__(self) -> str:
        return (
            f"<Blacklist(id={self.id}, ip={self.ip_address}, "
            f"reason='{self.reason}', active={self.is_active}, "
            f"expires={self.expires_at})>"
        )
