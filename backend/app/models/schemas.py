"""Pydantic schemas for request/response validation."""

import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


# Common validation functions
def validate_positive_amount(v):
    """Ensure amount is positive."""
    if v is not None and v <= 0:
        raise ValueError("Amount must be greater than zero")
    return v


def validate_positive_shares(v):
    """Ensure shares is positive if provided."""
    if v is not None and v <= 0:
        raise ValueError("Shares must be greater than zero")
    return v


# Enums
class AssetCategory(str, Enum):
    """Supported asset categories."""
    CASH = "cash"
    STOCK = "stock"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    BOND = "bond"
    OTHER = "other"


class CreditCategory(str, Enum):
    """Supported credit categories."""
    CREDIT_CARD = "credit_card"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    LINE_OF_CREDIT = "line_of_credit"
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


# Credit Type Schemas  
class CreditTypeResponse(BaseSchema):
    """Schema for credit type response."""
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
    symbol: Optional[str] = Field(None, max_length=10, description="Stock symbol (e.g., AAPL) - for stock assets only")
    shares: Optional[float] = Field(None, gt=0, description="Number of shares - for stock assets only")
    is_market_tracked: Optional[bool] = Field(False, description="Whether this asset supports real-time price updates")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is positive."""
        return validate_positive_amount(v)
    
    @field_validator("shares")
    @classmethod
    def validate_shares(cls, v):
        """Ensure shares is positive if provided."""
        return validate_positive_shares(v)


class AssetUpdate(BaseSchema):
    """Schema for updating an asset."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[AssetCategory] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[Currency] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    # Market data fields
    symbol: Optional[str] = Field(None, max_length=10, description="Stock symbol (e.g., AAPL) - for stock assets only")
    shares: Optional[float] = Field(None, gt=0, description="Number of shares - for stock assets only")
    is_market_tracked: Optional[bool] = Field(None, description="Whether this asset supports real-time price updates")
    current_amount: Optional[Decimal] = Field(None, gt=0, description="Current market value")
    original_amount: Optional[Decimal] = Field(None, gt=0, description="Original purchase amount")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is positive."""
        return validate_positive_amount(v)
    
    @field_validator("shares")
    @classmethod
    def validate_shares(cls, v):
        """Ensure shares is positive if provided."""
        return validate_positive_shares(v)
    
    @field_validator("current_amount")
    @classmethod
    def validate_current_amount(cls, v):
        """Ensure current amount is positive if provided."""
        return validate_positive_amount(v)
    
    @field_validator("original_amount")
    @classmethod
    def validate_original_amount(cls, v):
        """Ensure original amount is positive if provided."""
        return validate_positive_amount(v)
    
    @model_validator(mode='after')
    def validate_stock_fields(self):
        """Validate that symbol and shares are only used with stock category."""
        # For updates, we need to be more careful since category might not be provided
        if self.category is not None and self.category != AssetCategory.STOCK:
            if self.symbol is not None:
                raise ValueError("Symbol can only be specified for stock assets")
            if self.shares is not None:
                raise ValueError("Shares can only be specified for stock assets")
        return self


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
    symbol: Optional[str]
    shares: Optional[float]
    # Market data fields
    original_amount: Optional[Decimal]
    current_amount: Optional[Decimal]
    last_price_update: Optional[datetime]
    is_market_tracked: bool
    converted_amount: Optional[Decimal] = Field(None, description="Amount converted to base currency")
    conversion_rate: Optional[Decimal] = Field(None, description="Exchange rate used for conversion")
    created_at: datetime
    updated_at: datetime


# Credit Schemas
class CreditCreate(BaseSchema):
    """Schema for creating a credit."""
    name: str = Field(..., min_length=1, max_length=255, description="Credit name")
    category: CreditCategory = Field(..., description="Credit category")
    amount: Decimal = Field(..., gt=0, description="Credit amount owed")
    currency: Currency = Field(..., description="Credit currency")
    issue_date: date = Field(..., description="Credit issue/origination date")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is positive."""
        return validate_positive_amount(v)


class CreditUpdate(BaseSchema):
    """Schema for updating a credit."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[CreditCategory] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[Currency] = None
    issue_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is positive."""
        return validate_positive_amount(v)


class CreditResponse(BaseSchema):
    """Schema for credit response."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    category: str
    amount: Decimal
    currency: str
    issue_date: date
    notes: Optional[str]
    converted_amount: Optional[Decimal] = Field(None, description="Amount converted to base currency")
    conversion_rate: Optional[Decimal] = Field(None, description="Exchange rate used for conversion")
    created_at: datetime
    updated_at: datetime


# Portfolio Schemas
class AssetBreakdown(BaseSchema):
    """Schema for asset breakdown in portfolio."""
    total_amount: Decimal = Field(..., description="Total amount in base currency")
    count: int = Field(..., ge=0, description="Number of assets in this category")


class CreditBreakdown(BaseSchema):
    """Schema for credit breakdown in portfolio."""
    total_amount: Decimal = Field(..., description="Total amount owed in base currency")
    count: int = Field(..., ge=0, description="Number of credits in this category")


class AssetCategoryBreakdown(BaseSchema):
    """Schema for assets grouped by category with totals."""
    assets: List[AssetResponse] = Field(..., description="List of assets in this category")
    total_amount: Decimal = Field(..., description="Total amount in base currency")
    count: int = Field(..., ge=0, description="Number of assets in this category")


class CreditCategoryBreakdown(BaseSchema):
    """Schema for credits grouped by category with totals."""
    credits: List[CreditResponse] = Field(..., description="List of credits in this category")
    total_amount: Decimal = Field(..., description="Total amount owed in base currency")
    count: int = Field(..., ge=0, description="Number of credits in this category")


class PortfolioSummary(BaseSchema):
    """Schema for portfolio summary response."""
    base_currency: str = Field(..., description="Base currency for display")
    asset_summary: Dict[str, AssetBreakdown] = Field(..., description="Breakdown by asset category in base currency")
    credit_summary: Dict[str, CreditBreakdown] = Field(..., description="Breakdown by credit category in base currency")
    net_worth: Decimal = Field(..., description="Total net worth (assets - credits) in base currency")
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
    credit_categories: List[str]