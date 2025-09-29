"""Pydantic schemas for request/response validation."""

import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator, ConfigDict


# Enums
class AssetCategory(str, Enum):
    """Supported asset categories."""
    CASH = "cash"
    STOCK = "stock"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    OTHER = "other"


class Currency(str, Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CNY = "CNY"


# Base Schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
    )


# User Schemas
class UserCreate(BaseSchema):
    """Schema for creating a new user."""
    device_id: str = Field(..., min_length=1, max_length=255, description="Unique device identifier")


class UserResponse(BaseSchema):
    """Schema for user response."""
    id: uuid.UUID
    device_id: str
    created_at: datetime
    updated_at: datetime


# Asset Type Schemas  
class AssetTypeResponse(BaseSchema):
    """Schema for asset type response."""
    id: uuid.UUID
    name: str
    category: str
    is_default: bool
    created_at: datetime
    updated_at: datetime


# Asset Schemas
class AssetCreate(BaseSchema):
    """Schema for creating an asset."""
    name: str = Field(..., min_length=1, max_length=255, description="Asset name")
    category: AssetCategory = Field(..., description="Asset category")
    amount: Decimal = Field(..., gt=0, description="Asset amount/value")
    currency: Currency = Field(..., description="Asset currency")
    purchase_date: date = Field(..., description="Purchase date")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    
    @validator("amount")
    def validate_positive_amount(cls, v):
        """Ensure amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class AssetUpdate(BaseSchema):
    """Schema for updating an asset."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[AssetCategory] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[Currency] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator("amount")
    def validate_positive_amount(cls, v):
        """Ensure amount is positive."""
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class AssetResponse(BaseSchema):
    """Schema for asset response."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    category: str
    amount: Decimal
    currency: str
    purchase_date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# Portfolio Schemas
class AssetBreakdown(BaseSchema):
    """Schema for asset breakdown in portfolio."""
    total_amount: Decimal = Field(..., description="Total amount in original currency")
    count: int = Field(..., ge=0, description="Number of assets in this category")


class PortfolioSummary(BaseSchema):
    """Schema for portfolio summary response."""
    base_currency: str = Field(..., description="Base currency for display")
    asset_breakdown: Dict[str, AssetBreakdown] = Field(..., description="Breakdown by asset category")
    last_updated: datetime = Field(..., description="Last calculation timestamp")


# API Response Schemas
class SuccessResponse(BaseSchema):
    """Schema for success response."""
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseSchema):
    """Schema for error response."""
    error: str
    details: Optional[str] = None


# Metadata Schemas
class CurrencyInfo(BaseSchema):
    """Schema for currency information."""
    code: str
    name: str
    symbol: str


class MetadataResponse(BaseSchema):
    """Schema for metadata response."""
    currencies: List[CurrencyInfo]
    asset_categories: List[str]