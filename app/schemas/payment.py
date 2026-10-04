from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentInitializeRequest(BaseModel):
    order_id: int


class PaymentInitializeResponse(BaseModel):
    authorization_url: str
    access_code: str
    reference: str


class PaymentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    order_id: int
    reference: str
    provider: str
    status: str
    amount: Decimal
    currency: str
    paid_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PaginatedPaymentResponse(BaseModel):
    items: list[PaymentResponse]

    page: int
    page_size: int

    total: int
    total_pages: int
