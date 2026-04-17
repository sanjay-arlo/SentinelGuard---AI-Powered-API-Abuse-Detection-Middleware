"""Endpoint configuration model for per-endpoint rate limiting."""

from sqlalchemy import Column, String, Integer, Boolean, Index, DateTime

from ..base import BaseModel


class EndpointConfig(BaseModel):
    """Model for endpoint-specific rate limiting configurations."""
    
    __tablename__ = "endpoint_configs"
    
    endpoint_pattern = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Endpoint pattern (supports wildcards)"
    )
    
    rate_limit = Column(
        Integer,
        nullable=False,
        default=100,
        comment="Maximum requests per window"
    )
    
    window_seconds = Column(
        Integer,
        nullable=False,
        default=60,
        comment="Time window in seconds"
    )
    
    score_threshold = Column(
        Integer,
        nullable=False,
        default=50,
        comment="Risk score threshold for blocking"
    )
    
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default='true',
        comment="Whether this configuration is active"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_endpoint_configs_pattern', 'endpoint_pattern'),
        Index('idx_endpoint_configs_active', 'is_active'),
    )
    
    def matches_endpoint(self, endpoint: str) -> bool:
        """Check if this configuration matches the given endpoint."""
        import fnmatch
        
        if not self.is_active:
            return False
        
        return fnmatch.fnmatch(endpoint, self.endpoint_pattern)
    
    @property
    def requests_per_minute(self) -> float:
        """Calculate requests per minute rate."""
        return (self.rate_limit * 60) / self.window_seconds
    
    def __repr__(self) -> str:
        return (
            f"<EndpointConfig(id={self.id}, pattern='{self.endpoint_pattern}', "
            f"limit={self.rate_limit}/{self.window_seconds}s, "
            f"threshold={self.score_threshold}, active={self.is_active})>"
        )
