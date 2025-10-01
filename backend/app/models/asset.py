"""Asset-related models for financial tracking."""

import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from sqlalchemy import (
    String, Numeric, Date, DateTime, Boolean, ForeignKey,
    Index, UniqueConstraint, Text, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class AssetType(BaseModel):
    """
    Asset type definitions for categorization.
    
    Simple asset type model for basic categorization.
    """
    
    __tablename__ = "asset_types"
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Display name of the asset type"
    )
    
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Category for grouping (cash, stock, crypto, etc.)"
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is a system-provided default type"
    )
    
    # Relationships
    assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        back_populates="asset_type",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<AssetType(id={self.id}, name={self.name}, category={self.category})>"


class Asset(BaseModel):
    """
    Simple asset records for financial tracking.
    
    Basic asset model focused on essential financial data.
    """
    
    __tablename__ = "assets"
    
    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Owner of this asset"
    )
    
    asset_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("asset_types.id"),
        nullable=False,
        index=True,
        doc="Type of this asset"
    )
    
    # Core Asset Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="User-friendly name of the asset"
    )
    
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Asset category (cash, stock, crypto, etc.)"
    )
    
    # Financial Information
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 4),
        nullable=False,
        doc="Total amount/value of the asset"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        doc="Currency of the asset (ISO code)"
    )
    
    purchase_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Date of purchase/acquisition"
    )
    
    # Optional Information
    notes: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Optional notes about the asset"
    )
    
   # Market Data Fields (optional)
    symbol: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        doc="Stock symbol (e.g., AAPL, TSLA) - used for stock assets"
    )
    
    shares: Mapped[Optional[float]] = mapped_column(
        Numeric(15, 6),
        nullable=True,
        doc="Number of shares/quantity - used for stock assets"
    )
    
    original_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        nullable=True,
        doc="Original purchase amount (preserved for comparison)"
    )
    
    current_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 4),
        nullable=True,
        doc="Current market value (calculated from market_price * shares)"
    )
    
    last_price_update: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="Timestamp of last update like price updates"
    )
    
    is_market_tracked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether to track based on real-time price, selected by user"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="assets",
        lazy="select"
    )
    
    asset_type: Mapped["AssetType"] = relationship(
        "AssetType",
        back_populates="assets",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Asset(id={self.id}, name={self.name}, category={self.category}, amount={self.amount})>"


# # Create additional indexes for performance
# Index('ix_assets_user_id', Asset.user_id)
# Index('ix_assets_asset_type_id', Asset.asset_type_id)
# Index('ix_assets_category', Asset.category)
# Index('ix_assets_purchase_date', Asset.purchase_date)
# Index('ix_asset_types_category', AssetType.category)