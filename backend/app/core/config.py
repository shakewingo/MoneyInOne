"""Application configuration settings."""

import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = Field(default="MoneyInOne API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed hosts for CORS")
    
    # Database
    database_url: str = Field(
        # default="postgresql+asyncpg://postgres:postgres@localhost:5432/moneyinone",
        default="sqlite+aiosqlite:///./moneyinone.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # External APIs
    exchange_rate_api_key: Optional[str] = Field(
        default=None,
        description="Exchange rate API key"
    )
    yahoo_finance_timeout: int = Field(
        default=10,
        description="Yahoo Finance API timeout in seconds"
    )
    coingecko_timeout: int = Field(
        default=10,
        description="CoinGecko API timeout in seconds"
    )
    
    # Caching
    cache_ttl_exchange_rates: int = Field(
        default=3600,  # 1 hour
        description="Exchange rates cache TTL in seconds"
    )
    cache_ttl_asset_prices: int = Field(
        default=300,  # 5 minutes
        description="Asset prices cache TTL in seconds"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="Secret key for JWT tokens"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        allowed_schemes = (
            "postgresql://", "postgresql+asyncpg://",  # PostgreSQL
            "sqlite://", "sqlite+aiosqlite:///"        # SQLite
        )
        if not v.startswith(allowed_schemes):
            raise ValueError("Database URL must be PostgreSQL or SQLite")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()