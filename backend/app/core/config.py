"""Application configuration settings."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    debug: bool = Field(default=False, description="Enable debug mode")
    api_version: str = Field(default="v1", description="API version")
    project_name: str = Field(default="MoneyInOne API", description="Project name")

    # Database Settings
    database_url: str = Field(
        default="postgresql://moneyinone:password@localhost:5432/moneyinone",
        description="PostgreSQL database URL",
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=30, description="Database max overflow connections")

    # Redis Settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # External API Keys
    yahoo_finance_api_key: str = Field(default="", description="Yahoo Finance API key")
    alpha_vantage_api_key: str = Field(default="", description="Alpha Vantage API key")
    exchange_rate_api_key: str = Field(default="", description="Exchange Rate API key")
    coingecko_api_key: str = Field(default="", description="CoinGecko API key")

    # Security Settings
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0"],
        description="Allowed hosts for CORS and trusted host middleware",
    )

    # Cache Settings
    price_cache_ttl: int = Field(default=300, description="Price data cache TTL in seconds")
    crypto_cache_ttl: int = Field(default=60, description="Crypto price cache TTL in seconds")
    exchange_rate_cache_ttl: int = Field(default=3600, description="Exchange rate cache TTL in seconds")

    # API Rate Limiting
    api_rate_limit_requests: int = Field(default=100, description="API rate limit requests per minute")
    external_api_timeout: int = Field(default=10, description="External API timeout in seconds")

    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy."""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")


# Global settings instance
settings = Settings()
