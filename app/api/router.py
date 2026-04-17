"""Main API router aggregation for SentinelGuard."""

from fastapi import APIRouter

from .routes.health import router as health_router
from .routes.admin import router as admin_router
# Import other routers when they are implemented
# from .routes.monitor import router as monitor_router
# from .routes.proxy import router as proxy_router


api_router = APIRouter()

# Include all API routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])

# Uncomment when other routers are implemented
# api_router.include_router(monitor_router, prefix="/monitor", tags=["Monitor"])
# api_router.include_router(proxy_router, prefix="/proxy", tags=["Proxy"])
