"""Pydantic schemas for request/response validation."""

import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer,
    model_validator,
    ConfigDict,
)


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
    GOLD = "gold"
    SILVER = "silver"
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
        # Add JSON encoders to serialize Decimal as float for JSON responses
        json_encoders={Decimal: lambda v: float(v) if v is not None else None},
    )

    @field_serializer(
        "created_at",
        "updated_at",
        "purchase_date",
        "issue_date",
        "last_price_update",
        when_used="json",
        check_fields=False,
    )
    def serialize_date_as_datetime(self, value: date) -> str:
        """Serialize date fields as ISO 8601 datetime strings for frontend compatibility.

        Converts date-only values (e.g., 2025-10-01) to datetime strings with time
        (e.g., 2025-10-01T00:00:00Z) so Swift's default JSONDecoder can parse them.

        Args:
            value: The date value to serialize

        Returns:
            ISO 8601 datetime string with Z timezone indicator
        """
        if value is None:
            return None
        # Handle date objects - convert to datetime at midnight
        if isinstance(value, date) and not isinstance(value, datetime):
            dt = datetime.combine(value, datetime.min.time())
        # Handle datetime objects - remove microseconds
        else:
            dt = value.replace(microsecond=0)
        return dt.isoformat() + "Z"


# User Schemas
class UserCreate(BaseSchema):
    """Schema for creating a new user."""

    device_id: str = Field(
        ..., min_length=1, max_length=255, description="Unique device identifier"
    )


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
    symbol: Optional[str] = Field(
        None,
        max_length=10,
        description="Stock symbol (e.g., AAPL) - for stock assets only",
    )
    shares: Optional[float] = Field(
        None, gt=0, description="Number of shares - for stock assets only"
    )
    is_market_tracked: Optional[bool] = Field(
        False, description="Whether this asset supports real-time price updates"
    )

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

    @model_validator(mode="after")
    def enforce_usd_for_stock_crypto(self):
        """Ensure stock/crypto assets use USD only.

        Raises:
            ValueError: If category is stock/crypto and currency is not USD
        """
        if self.category in (AssetCategory.STOCK, AssetCategory.CRYPTO, AssetCategory.GOLD, AssetCategory.SILVER) and self.currency != Currency.USD:
            raise ValueError("Stock and crypto assets must use USD currency")
        return self


class AssetUpdate(BaseSchema):
    """Schema for updating an asset."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[AssetCategory] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[Currency] = None
    purchase_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    # Market data fields
    symbol: Optional[str] = Field(
        None,
        max_length=10,
        description="Stock symbol (e.g., AAPL) - for stock assets only",
    )
    shares: Optional[float] = Field(
        None, gt=0, description="Number of shares - for stock assets only"
    )
    is_market_tracked: Optional[bool] = Field(
        None, description="Whether this asset supports real-time price updates"
    )

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

    # Removed fields: current_amount, original_amount

    @model_validator(mode="after")
    def validate_stock_fields(self):
        """Allow symbol/shares for stock, crypto, gold, and silver; forbid otherwise when category provided."""
        # For updates, category might not be provided; only enforce when present
        allowed = (AssetCategory.STOCK, AssetCategory.CRYPTO, AssetCategory.GOLD, AssetCategory.SILVER)
        if self.category is not None and self.category not in allowed:
            if self.symbol is not None:
                raise ValueError("Symbol can only be specified for stock, crypto, gold, or silver assets")
            if self.shares is not None:
                raise ValueError("Shares can only be specified for stock, crypto, gold, or silver assets")
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
    # Market data fields removed: original_amount, current_amount
    last_price_update: Optional[datetime]
    is_market_tracked: bool
    converted_amount: Optional[Decimal] = Field(
        None, description="Amount converted to base currency"
    )
    conversion_rate: Optional[Decimal] = Field(
        None, description="Exchange rate used for conversion"
    )
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
    converted_amount: Optional[Decimal] = Field(
        None, description="Amount converted to base currency"
    )
    conversion_rate: Optional[Decimal] = Field(
        None, description="Exchange rate used for conversion"
    )
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

    assets: List[AssetResponse] = Field(
        ..., description="List of assets in this category"
    )
    total_amount: Decimal = Field(..., description="Total amount in base currency")
    count: int = Field(..., ge=0, description="Number of assets in this category")


class CreditCategoryBreakdown(BaseSchema):
    """Schema for credits grouped by category with totals."""

    credits: List[CreditResponse] = Field(
        ..., description="List of credits in this category"
    )
    total_amount: Decimal = Field(..., description="Total amount owed in base currency")
    count: int = Field(..., ge=0, description="Number of credits in this category")


class PortfolioSummary(BaseSchema):
    """Schema for portfolio summary response."""

    base_currency: str = Field(..., description="Base currency for display")
    asset_summary: Dict[str, AssetBreakdown] = Field(
        ..., description="Breakdown by asset category in base currency"
    )
    credit_summary: Dict[str, CreditBreakdown] = Field(
        ..., description="Breakdown by credit category in base currency"
    )
    net_worth: Decimal = Field(
        ..., description="Total net worth (assets - credits) in base currency"
    )
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
