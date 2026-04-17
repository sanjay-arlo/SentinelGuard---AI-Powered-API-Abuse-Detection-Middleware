"""Dependency injection for SentinelGuard API."""

from typing import Generator, Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_async_session
from ..utils.redis_client import get_redis_client
from ..core.config import settings
from ..core.security import verify_api_key

# HTTP Bearer for API key authentication
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator:
    """Get database session dependency."""
    async for session in get_async_session():
        yield session


async def get_async_session_dep() -> Generator[AsyncSession, None, None]:
    """Dependency to get async database session."""
    async with get_async_session() as session:
        yield session


async def get_redis():
    """Get Redis client dependency."""
    return get_redis_client()


async def get_current_admin_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """Dependency to authenticate admin users."""
    # Check for API key in header
    api_key = None
    
    if credentials:
        api_key = credentials.credentials
    elif "X-Admin-API-Key" in request.headers:
        api_key = request.headers["X-Admin-API-Key"]
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify API key
    if not verify_api_key(api_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user info (in a real app, you'd decode a JWT or look up user)
    return {
        "username": "admin",
        "role": "admin",
        "authenticated": True
    }


async def get_client_ip(request: Request) -> str:
    """Dependency to get client IP address."""
    # Check for forwarded headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the list
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"
