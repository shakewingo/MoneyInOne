"""Asset and AssetType models."""

from decimal import Decimal
from typing import Optional, Any, Dict
from datetime import date

from sqlalchemy import String, Numeric, Date, Boolean, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AssetType(Base, UUIDMixin, TimestampMixin):
    """Asset type definition with flexible attributes."""
    
    __tablename__ = "asset_types"
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Display name of the asset type (e.g., 'Stock', 'Cryptocurrency')"
    )
    
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Category identifier (e.g., 'stock', 'crypto', 'bond', 'cash')"
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether this is a default system asset type"
    )
    
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Flexible schema for type-specific attributes and validation rules"
    )
    
    # Relationships
    assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="asset_type",
        doc="Assets of this type"
    )
    
    def __repr__(self) -> str:
        """String representation of AssetType."""
        return f"<AssetType(id={self.id}, name='{self.name}', category='{self.category}')>"


class Asset(Base, UUIDMixin, TimestampMixin):
    """Individual asset owned by a user."""
    
    __tablename__ = "assets"
    
    # Foreign Keys
    user_id: Mapped[UUIDMixin.id] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the owning user"
    )
    
    asset_type_id: Mapped[UUIDMixin.id] = mapped_column(
        ForeignKey("asset_types.id"),
        nullable=False,
        index=True,
        doc="Reference to the asset type"
    )
    
    # Basic Asset Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Display name of the asset (e.g., 'Apple Inc.', 'Bitcoin')"
    )
    
    symbol: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True,
        doc="Trading symbol or ticker (e.g., 'AAPL', 'BTC')"
    )
    
    # Quantity and Pricing
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
        doc="Quantity owned (supports up to 8 decimal places for crypto)"
    )
    
    purchase_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 4),
        nullable=False,
        doc="Original purchase price per unit"
    )
    
    purchase_currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        doc="ISO 4217 currency code for purchase price"
    )
    
    purchase_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Date when the asset was purchased"
    )
    
    # Flexible Attributes
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        doc="Asset-specific data (shares, wallet_address, property_details, etc.)"
    )
    
    tags: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        doc="Array of tags for organization and filtering"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="assets",
        doc="User who owns this asset"
    )
    
    asset_type: Mapped["AssetType"] = relationship(
        "AssetType",
        back_populates="assets",
        doc="Type definition for this asset"
    )
    
    @property
    def total_cost(self) -> Decimal:
        """Calculate total cost in original currency."""
        return self.quantity * self.purchase_price
    
    def __repr__(self) -> str:
        """String representation of Asset."""
        return (
            f"<Asset(id={self.id}, name='{self.name}', "
            f"symbol='{self.symbol}', quantity={self.quantity})>"
        )
