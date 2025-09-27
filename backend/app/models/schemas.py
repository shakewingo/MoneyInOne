"""Pydantic schemas for request/response validation."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, validator


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


# User schemas
class UserBase(BaseSchema):
    """Base user schema."""
    device_id: str = Field(..., description="Unique device identifier")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    created_at: datetime
    updated_at: datetime


# Asset Type schemas
class AssetTypeBase(BaseSchema):
    """Base asset type schema."""
    name: str = Field(..., max_length=100, description="Display name of the asset type")
    category: str = Field(..., max_length=50, description="Category identifier")
    is_default: bool = Field(default=False, description="Whether this is a default system type")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Type-specific attributes")


class AssetTypeCreate(AssetTypeBase):
    """Schema for creating a new asset type."""
    pass


class AssetTypeResponse(AssetTypeBase):
    """Schema for asset type response."""
    id: UUID
    created_at: datetime
    updated_at: datetime


# Asset schemas
class AssetBase(BaseSchema):
    """Base asset schema."""
    name: str = Field(..., max_length=255, description="Display name of the asset")
    symbol: Optional[str] = Field(None, max_length=20, description="Trading symbol or ticker")
    quantity: Decimal = Field(..., gt=0, description="Quantity owned")
    purchase_price: Decimal = Field(..., gt=0, description="Original purchase price per unit")
    purchase_currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code")
    purchase_date: date = Field(..., description="Date when the asset was purchased")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Asset-specific data")
    tags: Optional[List[str]] = Field(None, description="Tags for organization")
    
    @validator('purchase_currency')
    def validate_currency_code(cls, v: str) -> str:
        """Validate currency code format."""
        if not v.isupper():
            raise ValueError('Currency code must be uppercase')
        return v
    
    @validator('tags')
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and clean tags."""
        if v is None:
            return v
        # Remove duplicates and empty strings
        cleaned = list(dict.fromkeys(tag.strip() for tag in v if tag.strip()))
        return cleaned if cleaned else None


class AssetCreate(AssetBase):
    """Schema for creating a new asset."""
    asset_type_id: UUID = Field(..., description="Reference to the asset type")


class AssetUpdate(BaseSchema):
    """Schema for updating an asset."""
    name: Optional[str] = Field(None, max_length=255)
    symbol: Optional[str] = Field(None, max_length=20)
    quantity: Optional[Decimal] = Field(None, gt=0)
    purchase_price: Optional[Decimal] = Field(None, gt=0)
    purchase_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    purchase_date: Optional[date] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    @validator('purchase_currency')
    def validate_currency_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code format."""
        if v is not None and not v.isupper():
            raise ValueError('Currency code must be uppercase')
        return v


class AssetResponse(AssetBase):
    """Schema for asset response."""
    id: UUID
    user_id: UUID
    asset_type_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Calculated fields (will be added by service layer)
    current_price: Optional[Decimal] = Field(None, description="Current market price")
    current_value: Optional[Decimal] = Field(None, description="Current total value")
    gain_loss: Optional[Decimal] = Field(None, description="Absolute gain/loss")
    gain_loss_percent: Optional[Decimal] = Field(None, description="Percentage gain/loss")
    
    # Related data
    asset_type: Optional[AssetTypeResponse] = None


# Price schemas
class AssetPriceBase(BaseSchema):
    """Base asset price schema."""
    symbol: str = Field(..., max_length=20)
    asset_type: str = Field(..., max_length=50)
    price: Decimal = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    source: str = Field(..., max_length=50)
    change_24h: Optional[Decimal] = None
    volume_24h: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None


class AssetPriceResponse(AssetPriceBase):
    """Schema for asset price response."""
    id: UUID
    fetched_at: datetime


class ExchangeRateBase(BaseSchema):
    """Base exchange rate schema."""
    from_currency: str = Field(..., min_length=3, max_length=3)
    to_currency: str = Field(..., min_length=3, max_length=3)
    rate: Decimal = Field(..., gt=0)
    source: str = Field(..., max_length=50)


class ExchangeRateResponse(ExchangeRateBase):
    """Schema for exchange rate response."""
    id: UUID
    fetched_at: datetime


# Portfolio schemas
class PortfolioSummary(BaseSchema):
    """Portfolio summary response schema."""
    total_value: Dict[str, Decimal] = Field(..., description="Total value in different currencies")
    total_gain_loss: Dict[str, Any] = Field(..., description="Total gain/loss amount and percentage")
    asset_allocation: List[Dict[str, Any]] = Field(..., description="Asset allocation breakdown")
    asset_count: int = Field(..., description="Total number of assets")
    last_updated: datetime = Field(..., description="When portfolio was last calculated")


# API Response schemas
class APIResponse(BaseSchema):
    """Generic API response wrapper."""
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages if any")


class PaginatedResponse(BaseSchema):
    """Paginated response wrapper."""
    items: List[Any] = Field(..., description="List of items")
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    @validator('total_pages', pre=True, always=True)
    def calculate_total_pages(cls, v, values):
        """Calculate total pages based on total_count and page_size."""
        total_count = values.get('total_count', 0)
        page_size = values.get('page_size', 1)
        return (total_count + page_size - 1) // page_size if page_size > 0 else 0
