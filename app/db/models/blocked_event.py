"""Blocked event model for audit trail."""

from sqlalchemy import Column, String, Integer, BigInteger, Text, Boolean, Index, DateTime
from sqlalchemy.dialects.postgresql import INET, ARRAY

from ..base import BaseModel


class BlockedEvent(BaseModel):
    """Model for tracking blocked events for audit trail."""
    
    __tablename__ = "blocked_events"
    
    ip_address = Column(
        INET,
        nullable=False,
        comment="Blocked IP address"
    )
    
    fingerprint_hash = Column(
        String(64),
        nullable=False,
        comment="SHA256 hash of request fingerprint"
    )
    
    endpoint = Column(
        String(255),
        nullable=False,
        comment="API endpoint that was blocked"
    )
    
    risk_score = Column(
        Integer,
        nullable=False,
        comment="Risk score at time of blocking"
    )
    
    block_reasons = Column(
        ARRAY(Text),
        nullable=False,
        comment="Array of reasons for blocking"
    )
    
    blocked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default='NOW()',
        comment="When the block occurred"
    )
    
    unblocked_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the block was lifted"
    )
    
    auto_unblocked = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default='false',
        comment="Whether unblocking was automatic"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blocked_events_ip', 'ip_address'),
        Index('idx_blocked_events_blocked_at', 'blocked_at'),
        Index('idx_blocked_events_fingerprint', 'fingerprint_hash'),
        Index('idx_blocked_events_endpoint', 'endpoint'),
        Index('idx_blocked_events_composite', 'ip_address', 'blocked_at'),
    )
    
    @property
    def is_active_block(self) -> bool:
        """Check if this block is still active."""
        if self.unblocked_at is None:
            return True
        
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) < self.unblocked_at
    
    @property
    def block_duration_minutes(self) -> int:
        """Calculate block duration in minutes."""
        if self.unblocked_at is None:
            return 0
        
        duration = self.unblocked_at - self.blocked_at
        return int(duration.total_seconds() / 60)
    
    def mark_unblocked(self, auto: bool = False) -> None:
        """Mark this event as unblocked."""
        from datetime import datetime, timezone
        self.unblocked_at = datetime.now(timezone.utc)
        self.auto_unblocked = auto
    
    def __repr__(self) -> str:
        return (
            f"<BlockedEvent(id={self.id}, ip={self.ip_address}, "
            f"endpoint={self.endpoint}, score={self.risk_score}, "
            f"reasons={self.block_reasons}, active={self.is_active_block})>"
        )
