"""Whitelist model for trusted IP addresses."""

from sqlalchemy import Column, String, Index, DateTime
from sqlalchemy.dialects.postgresql import INET

from ..base import BaseModel


class Whitelist(BaseModel):
    """Model for IP whitelist entries."""
    
    __tablename__ = "whitelist"
    
    ip_address = Column(
        INET,
        nullable=False,
        unique=True,
        comment="Whitelisted IP address"
    )
    
    note = Column(
        String(500),
        nullable=True,
        comment="Notes about why this IP is whitelisted"
    )
    
    added_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default='NOW()',
        comment="When the IP was added to whitelist"
    )
    
    added_by = Column(
        String(100),
        nullable=False,
        default='system',
        server_default='system',
        comment="Who added the IP (system or admin)"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_whitelist_ip', 'ip_address'),
        Index('idx_whitelist_added_at', 'added_at'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Whitelist(id={self.id}, ip={self.ip_address}, "
            f"note='{self.note}', added_by={self.added_by})>"
        )
