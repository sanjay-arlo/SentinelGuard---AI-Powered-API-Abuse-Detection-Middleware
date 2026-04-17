"""Custom exceptions for SentinelGuard."""

from typing import Dict, Any, Optional

from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_403_FORBIDDEN


class SentinelException(Exception):
    """Base exception for SentinelGuard."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self,
        limit: int,
        remaining: int,
        reset_time: int,
        retry_after: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.limit = limit
        self.remaining = remaining
        self.reset_time = reset_time
        self.retry_after = retry_after
        
        # Build response headers
        response_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }
        
        if retry_after:
            response_headers["Retry-After"] = str(retry_after)
        
        if headers:
            response_headers.update(headers)
        
        super().__init__(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "limit": limit,
                "remaining": remaining,
                "reset_time": reset_time,
                "retry_after": retry_after,
            },
            headers=response_headers,
        )


class BlockedBySentinel(HTTPException):
    """Exception raised when a request is blocked by SentinelGuard."""
    
    def __init__(
        self,
        reason: str,
        risk_score: int,
        fingerprint: str,
        block_duration_minutes: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.reason = reason
        self.risk_score = risk_score
        self.fingerprint = fingerprint
        self.block_duration_minutes = block_duration_minutes
        
        # Build response headers
        response_headers = {
            "X-Sentinel-Score": str(risk_score),
            "X-Sentinel-Fingerprint": fingerprint,
            "X-Sentinel-Block-Reason": reason,
        }
        
        if block_duration_minutes:
            response_headers["X-Sentinel-Block-Duration"] = str(block_duration_minutes)
            response_headers["Retry-After"] = str(block_duration_minutes * 60)
        
        if headers:
            response_headers.update(headers)
        
        super().__init__(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Request blocked by SentinelGuard",
                "reason": reason,
                "risk_score": risk_score,
                "fingerprint": fingerprint,
                "block_duration_minutes": block_duration_minutes,
            },
            headers=response_headers,
        )


class BlacklistedIP(HTTPException):
    """Exception raised when IP is blacklisted."""
    
    def __init__(
        self,
        ip_address: str,
        reason: str,
        blocked_at: str,
        expires_at: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.ip_address = ip_address
        self.reason = reason
        self.blocked_at = blocked_at
        self.expires_at = expires_at
        
        # Build response headers
        response_headers = {
            "X-Sentinel-Blacklisted": "true",
            "X-Sentinel-Block-Reason": reason,
            "X-Sentinel-Blocked-At": blocked_at,
        }
        
        if expires_at:
            response_headers["X-Sentinel-Expires-At"] = expires_at
            # Calculate retry-after from expires_at
            try:
                from datetime import datetime
                expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                retry_after = int(expiry.timestamp() - datetime.utcnow().timestamp())
                if retry_after > 0:
                    response_headers["Retry-After"] = str(retry_after)
            except (ValueError, TypeError):
                pass
        
        if headers:
            response_headers.update(headers)
        
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail={
                "error": "IP address is blacklisted",
                "ip_address": ip_address,
                "reason": reason,
                "blocked_at": blocked_at,
                "expires_at": expires_at,
            },
            headers=response_headers,
        )


class ConfigurationError(SentinelException):
    """Exception raised for configuration errors."""
    
    pass


class DatabaseError(SentinelException):
    """Exception raised for database operation errors."""
    
    pass


class RedisError(SentinelException):
    """Exception raised for Redis operation errors."""
    
    pass


class DownstreamServiceError(SentinelException):
    """Exception raised when downstream service is unavailable."""
    
    pass


class FingerprintGenerationError(SentinelException):
    """Exception raised when fingerprint generation fails."""
    
    pass


class InvalidEndpointPattern(SentinelException):
    """Exception raised when endpoint pattern is invalid."""
    
    pass


class AuthenticationError(HTTPException):
    """Exception raised for authentication failures."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=HTTP_401_FORBIDDEN,
            detail={
                "error": "Authentication failed",
                "message": detail,
            },
        )


class AuthorizationError(HTTPException):
    """Exception raised for authorization failures."""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied", 
                "message": detail,
            },
        )
