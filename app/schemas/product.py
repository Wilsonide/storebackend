from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product_variant import (
    ProductVariantCreate,
    ProductVariantResponse,
)


class ProductBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    description: str = Field(
        ...,
        min_length=1,
    )

    category_id: int

    brand_id: int | None = None

    material: str | None = Field(
        default=None,
        max_length=100,
    )

    gender: str | None = Field(
        default=None,
        max_length=50,
    )

    warranty: str | None = Field(
        default=None,
        max_length=255,
    )

    cover_image: str | None = Field(
        default=None,
        max_length=500,
    )

    cover_public_id: str | None = Field(
        default=None,
        max_length=255,
    )

    is_available: bool = True

    is_featured: bool = False


class ProductCreate(ProductBase):
    variants: list[ProductVariantCreate] = Field(
        default_factory=list,
    )


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    category_id: int | None = None

    brand_id: int | None = None

    material: str | None = None

    gender: str | None = None

    warranty: str | None = None

    cover_image: str | None = None

    cover_public_id: str | None = None

    is_available: bool | None = None

    is_featured: bool | None = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    variants: list[ProductVariantResponse] = Field(
        default_factory=list,
    )


class ProductListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cover_image: str | None
    is_available: bool
    is_featured: bool
    category_id: int
    brand_id: int | None


class ProductQueryParams(BaseModel):
    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    search: str | None = Field(
        default=None,
        max_length=100,
    )

    category_id: int | None = None

    brand_id: int | None = None

    featured: bool | None = None

    available: bool | None = True

    min_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    max_price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    sort: Literal[
        "newest",
        "oldest",
        "price_asc",
        "price_desc",
        "name_asc",
        "name_desc",
    ] = "newest"


class PaginatedProductResponse(BaseModel):
    items: list[ProductListResponse]

    page: int
    page_size: int

    total: int
    total_pages: int

    has_next: bool
    has_previous: bool
