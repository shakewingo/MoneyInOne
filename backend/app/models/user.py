"""User model for future multi-user support."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User model for device-based identification."""
    
    __tablename__ = "users"
    
    device_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique device identifier for iOS device"
    )
    
    # Relationships
    assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="Assets owned by this user"
    )
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, device_id='{self.device_id}')>"
