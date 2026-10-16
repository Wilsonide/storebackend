
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    public_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    is_cover: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    product = relationship(
        "Product",
        back_populates="images",
    )
