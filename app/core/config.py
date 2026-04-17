"""Configuration management for SentinelGuard."""

import os
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = Field(default="SentinelGuard", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    admin_api_key: str = Field(default="change-me-in-production", env="ADMIN_API_KEY")
    
    # Database
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_name: str = Field(default="sentinelguard", env="DB_NAME")
    db_user: str = Field(default="sentinel", env="DB_USER")
    db_password: str = Field(default="change-me", env="DB_PASSWORD")
    db_pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    
    # Redis
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    
    # Rate Limiting Defaults
    default_rate_limit: int = Field(default=100, env="DEFAULT_RATE_LIMIT")
    default_window_seconds: int = Field(default=60, env="DEFAULT_WINDOW_SECONDS")
    default_score_threshold: int = Field(default=50, env="DEFAULT_SCORE_THRESHOLD")
    default_block_duration_minutes: int = Field(default=10, env="DEFAULT_BLOCK_DURATION_MINUTES")
    max_block_duration_minutes: int = Field(default=60, env="MAX_BLOCK_DURATION_MINUTES")
    score_decay_seconds: int = Field(default=300, env="SCORE_DECAY_SECONDS")
    
    # Downstream API
    downstream_api_url: str = Field(default="http://localhost:8001", env="DOWNSTREAM_API_URL")
    downstream_api_timeout: int = Field(default=30, env="DOWNSTREAM_API_TIMEOUT")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Security
    trusted_proxies: str = Field(
        default="nginx,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16",
        env="TRUSTED_PROXIES"
    )
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator("trusted_proxies")
    def parse_trusted_proxies(cls, v: str) -> List[str]:
        """Parse trusted proxies string into list."""
        return [proxy.strip() for proxy in v.split(",") if proxy.strip()]
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """Construct synchronous PostgreSQL database URL for Alembic."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
