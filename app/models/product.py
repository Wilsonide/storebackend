from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False,
        index=True,
    )

    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey("brands.id"),
        nullable=True,
        index=True,
    )

    # --------------------------------------------------------
    # GENERAL PRODUCT INFORMATION
    # --------------------------------------------------------

    material: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    warranty: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # --------------------------------------------------------
    # PRODUCT IMAGE
    # --------------------------------------------------------

    cover_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    cover_public_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # --------------------------------------------------------
    # TIMESTAMPS
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    category = relationship(
        "Category",
        back_populates="products",
    )

    brand = relationship(
        "Brand",
        back_populates="products",
    )
    images = relationship(
    "ProductImage",
    back_populates="product",
    cascade="all, delete-orphan",
    order_by="ProductImage.sort_order",
)

    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
    )
