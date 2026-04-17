"""Health check endpoints for SentinelGuard."""

import time
from typing import Dict, Any

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from ...core.config import settings
from ...db.session import check_database_connection
from ...utils.redis_client import get_redis_client

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "uptime_seconds": int(time.time() - getattr(health_check, '_start_time', time.time())),
        "app_name": settings.app_name,
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe - check all dependencies."""
    checks = {}
    
    # Database check
    try:
        db_healthy = await check_database_connection()
        checks["database"] = "ok" if db_healthy else "error"
    except Exception:
        checks["database"] = "error"
    
    # Redis check
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"
    
    # Overall status
    all_healthy = all(status == "ok" for status in checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
    }


@router.get("/health/metrics", response_class=PlainTextResponse)
async def prometheus_metrics() -> str:
    """Prometheus metrics endpoint."""
    metrics = [
        "# HELP sentinelguard_uptime_seconds Application uptime in seconds",
        "# TYPE sentinelguard_uptime_seconds gauge",
        f"sentinelguard_uptime_seconds {int(time.time() - getattr(health_check, '_start_time', time.time()))}",
        "",
        "# HELP sentinelguard_version Application version",
        "# TYPE sentinelguard_version gauge",
        f'sentinelguard_version{{version="{settings.app_version}"}} 1',
        "",
        "# HELP sentinelguard_requests_total Total number of requests",
        "# TYPE sentinelguard_requests_total counter",
        "sentinelguard_requests_total 0",  # Will be implemented with actual metrics
        "",
    ]
    
    return "\n".join(metrics)


# Store startup time for uptime calculation
health_check._start_time = time.time()
