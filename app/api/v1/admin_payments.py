from fastapi import APIRouter, Query, status

from app.core.deps import (
    CurrentUser,
    DBSession,
)
from app.schemas.payment import PaginatedPaymentResponse, PaymentResponse
from app.services.payment_service import payment_service

router = APIRouter(
    prefix="/admin/payments",
    tags=["Admin Payments"],
)


# ============================================================
# GET ALL PAYMENTS
# ============================================================


@router.get(
    "",
    response_model=PaginatedPaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_payments(
    session: DBSession,
    current_user: CurrentUser,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    return await payment_service.get_all_payments(
        session,
        current_user,
        page,
        page_size,
    )


# ============================================================
# GET SINGLE PAYMENT
# ============================================================


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_admin_payment(
    payment_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    return await payment_service.get_admin_payment(
        session,
        current_user,
        payment_id,
    )
