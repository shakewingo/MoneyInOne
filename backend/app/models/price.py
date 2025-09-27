"""Price data models for caching external API responses."""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Numeric, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class ExchangeRate(Base, UUIDMixin):
    """Exchange rate data for currency conversion."""
    
    __tablename__ = "exchange_rates"
    
    from_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        doc="Source currency (ISO 4217 code)"
    )
    
    to_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        doc="Target currency (ISO 4217 code)"
    )
    
    rate: Mapped[Decimal] = mapped_column(
        Numeric(15, 8),
        nullable=False,
        doc="Exchange rate from source to target currency"
    )
    
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="API source that provided this rate (e.g., 'exchangerate-api')"
    )
    
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Timestamp when this rate was fetched from the API"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint(
            "from_currency", 
            "to_currency", 
            "fetched_at",
            name="uq_exchange_rate_currencies_date"
        ),
        Index("idx_exchange_rates_currencies", "from_currency", "to_currency"),
        Index("idx_exchange_rates_fetched_at", "fetched_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of ExchangeRate."""
        return (
            f"<ExchangeRate({self.from_currency}/{self.to_currency}={self.rate}, "
            f"source='{self.source}', fetched_at={self.fetched_at})>"
        )


class AssetPrice(Base, UUIDMixin):
    """Asset price data for caching external API responses."""
    
    __tablename__ = "asset_prices"
    
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        doc="Trading symbol or identifier (e.g., 'AAPL', 'BTC')"
    )
    
    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Asset type category (e.g., 'stock', 'crypto')"
    )
    
    price: Mapped[Decimal] = mapped_column(
        Numeric(15, 4),
        nullable=False,
        doc="Current price of the asset"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        doc="Currency of the price (ISO 4217 code)"
    )
    
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="API source that provided this price (e.g., 'yahoo_finance', 'coingecko')"
    )
    
    change_24h: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 4),
        nullable=True,
        doc="24-hour price change percentage"
    )
    
    volume_24h: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="24-hour trading volume"
    )
    
    market_cap: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(20, 2),
        nullable=True,
        doc="Market capitalization (for stocks/crypto)"
    )
    
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Timestamp when this price was fetched from the API"
    )
    
    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint(
            "symbol", 
            "asset_type", 
            "fetched_at",
            name="uq_asset_price_symbol_type_date"
        ),
        Index("idx_asset_prices_symbol_type", "symbol", "asset_type"),
        Index("idx_asset_prices_fetched_at", "fetched_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of AssetPrice."""
        return (
            f"<AssetPrice({self.symbol}={self.price} {self.currency}, "
            f"type='{self.asset_type}', source='{self.source}', "
            f"fetched_at={self.fetched_at})>"
        )
