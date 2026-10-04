import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .email_verification import EmailVerification
    from .refresh_token import RefreshToken


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    name: Mapped[str] = mapped_column(String(200))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="USER")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # 🔐 AUTH RELATIONSHIPS
    email_verification: Mapped["EmailVerification"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    refresh_token: Mapped["RefreshToken"] = relationship(
        back_populates="user",
        uselist=False,  # 🔐 1-to-1
        cascade="all, delete-orphan",
    )

    reviews = relationship("Review", back_populates="user", cascade="all, delete")
