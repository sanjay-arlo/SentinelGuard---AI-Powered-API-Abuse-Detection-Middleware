"""Redis client management for SentinelGuard."""

import redis.asyncio as redis
from typing import Optional

from ..core.config import settings
from ..core.exceptions import RedisError


# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
    
    return _redis_client


async def init_redis() -> None:
    """Initialize Redis connection."""
    try:
        client = get_redis_client()
        await client.ping()
        print("Redis connection initialized successfully")
    except Exception as e:
        raise RedisError(f"Failed to initialize Redis: {e}")


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        print("Redis connection closed")
