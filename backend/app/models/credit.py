"""Credit-related models for financial tracking."""

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


class CreditType(BaseModel):
    """
    Credit type definitions for categorization.
    
    Simple credit type model for basic categorization.
    """
    
    __tablename__ = "credit_types"
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Display name of the credit type"
    )
    
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Category for grouping (credit_card, loan, mortgage, etc.)"
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this is a system-provided default type"
    )
    
    # Relationships
    credits: Mapped[List["Credit"]] = relationship(
        "Credit",
        back_populates="credit_type",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<CreditType(id={self.id}, name={self.name}, category={self.category})>"


class Credit(BaseModel):
    """
    Simple credit records for financial tracking.
    
    Basic credit model focused on essential financial data.
    """
    
    __tablename__ = "credits"
    
    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Owner of this credit"
    )
    
    credit_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credit_types.id"),
        nullable=False,
        index=True,
        doc="Type of this credit"
    )
    
    # Core Credit Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="User-friendly name of the credit"
    )
    
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Credit category (credit_card, loan, mortgage, etc.)"
    )
    
    # Financial Information
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 4),
        nullable=False,
        doc="Total amount owed/credit balance"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        doc="Currency of the credit (ISO code)"
    )
    
    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Date of credit issue/origination"
    )
    
    # Optional Information
    notes: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Optional notes about the credit"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="credits",
        lazy="select"
    )
    
    credit_type: Mapped["CreditType"] = relationship(
        "CreditType",
        back_populates="credits",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<Credit(id={self.id}, name={self.name}, category={self.category}, amount={self.amount})>"
