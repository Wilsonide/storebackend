
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

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


class ProductImageCreate(BaseModel):
    image_url: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    public_id: str | None = Field(
        default=None,
        max_length=255,
    )

    sort_order: int = Field(
        default=0,
        ge=0,
    )

    is_cover: bool = False


class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    public_id: str | None
    product_id: int
    sort_order: int
    is_cover: bool


class ProductCreate(ProductBase):
    variants: list[ProductVariantCreate] = Field(
        default_factory=list,
    )

    images: list[ProductImageCreate] = Field(
        default_factory=list,
        max_length=10,
    )

    @model_validator(mode="after")
    def validate_images(self):
        covers = [image for image in self.images if image.is_cover]

        if len(covers) > 1:
            raise ValueError(
                "A product can have only one cover image."
            )

        return self


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
    )

    category_id: int | None = None
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

    is_available: bool | None = None
    is_featured: bool | None = None

    # None means do not modify the existing gallery.
    # An empty list means remove all gallery images.
    images: list[ProductImageCreate] | None = Field(
        default=None,
        max_length=10,
    )

    @model_validator(mode="after")
    def validate_images(self):
        if self.images is not None:
            covers = [
                image
                for image in self.images
                if image.is_cover
            ]

            if len(covers) > 1:
                raise ValueError(
                    "A product can have only one cover image."
                )

        return self


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    images: list[ProductImageResponse] = Field(
        default_factory=list,
    )

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

    images: list[ProductImageResponse] = Field(
        default_factory=list,
    )


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
