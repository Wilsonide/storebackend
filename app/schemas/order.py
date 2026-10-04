from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================
# CREATE
# ============================================================


class OrderItemCreate(BaseModel):
    variant_id: int = Field(
        ...,
        gt=0,
    )

    quantity: int = Field(
        ...,
        gt=0,
        le=100,
    )


class OrderCreate(BaseModel):
    shipping_address: str = Field(
        ...,
        min_length=5,
        max_length=500,
    )

    phone_number: str = Field(
        ...,
        min_length=7,
        max_length=20,
    )

    items: list[OrderItemCreate] = Field(
        ...,
        min_length=1,
        max_length=50,
    )


# ============================================================
# ORDER ITEM RESPONSE
# ============================================================


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    variant_id: int
    quantity: int
    price: Decimal


# ============================================================
# ORDER RESPONSE
# ============================================================


class OrderResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    total_amount: Decimal

    status: str

    payment_status: str

    shipping_address: str

    phone_number: str

    user_id: UUID

    created_at: datetime

    updated_at: datetime

    items: list[OrderItemResponse] = Field(
        default_factory=list,
    )


# ============================================================
# PAGINATED RESPONSE
# ============================================================


class OrderListResponse(BaseModel):
    items: list[OrderResponse]

    page: int
    page_size: int
    total: int
    total_pages: int
