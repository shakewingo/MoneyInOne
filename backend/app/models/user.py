"""User model for device-based authentication."""

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.credit import Credit


class User(BaseModel):
    """
    User model for device-based authentication.
    
    Each device gets a unique user record for data isolation.
    """
    
    __tablename__ = "users"
    
    # Device identifier (unique per installation)
    device_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique device identifier"
    )
    
    # Relationships
    assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    credits: Mapped[List["Credit"]] = relationship(
        "Credit",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, device_id={self.device_id})>"


# # Create additional indexes
# Index('ix_users_device_id', User.device_id)