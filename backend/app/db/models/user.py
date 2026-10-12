"""
User Model
Represents authenticated users (synced with Supabase Auth)
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    User model (mirrors Supabase auth.users)
    
    Note: This is primarily for foreign key relationships.
    Actual authentication is handled by Supabase Auth.
    """
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    
    # Relationships
    profile: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
