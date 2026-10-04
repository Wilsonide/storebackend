from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductVariantBase(BaseModel):
    price: Decimal = Field(
        ...,
        ge=0,
    )

    quantity: int = Field(
        default=0,
        ge=0,
    )

    color: str | None = Field(
        default=None,
        max_length=100,
    )

    size: str | None = Field(
        default=None,
        max_length=100,
    )

    is_default: bool = False

    is_available: bool = True


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(BaseModel):
    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    quantity: int | None = Field(
        default=None,
        ge=0,
    )

    color: str | None = Field(
        default=None,
        max_length=100,
    )

    size: str | None = Field(
        default=None,
        max_length=100,
    )

    material: str | None = Field(
        default=None,
        max_length=100,
    )

    style: str | None = Field(
        default=None,
        max_length=100,
    )

    strap_type: str | None = Field(
        default=None,
        max_length=100,
    )

    is_default: bool | None = None

    is_available: bool | None = None


class ProductVariantResponse(ProductVariantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
