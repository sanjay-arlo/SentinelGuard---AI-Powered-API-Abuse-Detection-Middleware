"""Main FastAPI application factory for SentinelGuard."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.exceptions import SentinelException
from .api.router import api_router
from .api.routes.health import router as health_router
from .utils.redis_client import get_redis_client
from .db.session import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Check database connection
    db_healthy = await check_database_connection()
    if not db_healthy:
        print("WARNING: Database connection failed")
    
    # Check Redis connection
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        print("Redis connection successful")
    except Exception as e:
        print(f"WARNING: Redis connection failed: {e}")
    
    print("Application startup complete")
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    # Close Redis connection
    try:
        redis_client = get_redis_client()
        await redis_client.close()
    except Exception:
        pass
    print("Application shutdown complete")


def create_app() -> FastAPI:
    """Create FastAPI application instance."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered API Abuse Detection Middleware",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    @app.exception_handler(SentinelException)
    async def sentinel_exception_handler(request: Request, exc: SentinelException) -> JSONResponse:
        """Handle SentinelGuard exceptions."""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": exc.message,
                "details": exc.details,
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        if settings.debug:
            import traceback
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                },
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
            )
    
    # Include routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Create application instance
app = create_app()
