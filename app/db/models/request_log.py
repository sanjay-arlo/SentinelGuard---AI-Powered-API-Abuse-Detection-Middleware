"""Request log model for tracking all requests."""

from sqlalchemy import Column, String, Text, Integer, BigInteger, Index, DateTime
from sqlalchemy.dialects.postgresql import INET

from ..base import BaseModel


class RequestLog(BaseModel):
    """Model for logging all incoming requests."""
    
    __tablename__ = "request_logs"
    
    fingerprint_hash = Column(
        String(64),
        nullable=False,
        comment="SHA256 hash of request fingerprint"
    )
    
    ip_address = Column(
        INET,
        nullable=False,
        comment="Client IP address"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="User-Agent string"
    )
    
    endpoint = Column(
        String(255),
        nullable=False,
        comment="API endpoint path"
    )
    
    method = Column(
        String(10),
        nullable=False,
        comment="HTTP method"
    )
    
    status = Column(
        String(20),
        nullable=False,
        comment="Request status: allowed, blocked, whitelisted"
    )
    
    risk_score = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Calculated risk score (0-100)"
    )
    
    block_reason = Column(
        String(255),
        nullable=True,
        comment="Reason for blocking if applicable"
    )
    
    response_time_ms = Column(
        Integer,
        nullable=True,
        comment="Response time in milliseconds"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_request_logs_fingerprint', 'fingerprint_hash'),
        Index('idx_request_logs_ip', 'ip_address'),
        Index('idx_request_logs_created_at', 'created_at'),
        Index('idx_request_logs_status', 'status'),
        Index('idx_request_logs_endpoint', 'endpoint'),
        Index('idx_request_logs_composite', 'ip_address', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<RequestLog(id={self.id}, ip={self.ip_address}, "
            f"endpoint={self.endpoint}, status={self.status}, "
            f"score={self.risk_score})>"
        )
