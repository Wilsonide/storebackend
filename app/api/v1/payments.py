from fastapi import APIRouter, status

from app.core.deps import (
    CurrentUser,
    DBSession,
)
from app.schemas.payment import (
    PaymentInitializeRequest,
    PaymentInitializeResponse,
    PaymentResponse,
)
from app.services.payment_service import (
    payment_service,
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


# ============================================================
# INITIALIZE
# ============================================================


@router.post(
    "/initialize",
    response_model=PaymentInitializeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def initialize_payment(
    data: PaymentInitializeRequest,
    session: DBSession,
    current_user: CurrentUser,
):
    result = await payment_service.initialize_payment(
        session,
        current_user,
        data.order_id,
    )

    await session.commit()

    return result


# ============================================================
# VERIFY
# ============================================================


@router.get(
    "/verify/{reference}",
    response_model=PaymentResponse,
)
async def verify_payment(
    reference: str,
    session: DBSession,
):
    payment = await payment_service.verify_payment(
        session,
        reference,
    )

    await session.commit()

    return payment


# ============================================================
# GET MY PAYMENTS
# ============================================================


@router.get(
    "/me",
    response_model=list[PaymentResponse],
)
async def my_payments(
    session: DBSession,
    current_user: CurrentUser,
):
    return await payment_service.get_user_payments(
        session,
        current_user,
    )


# ============================================================
# GET PAYMENT
# ============================================================


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
async def get_payment(
    payment_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    return await payment_service.get_payment(
        session,
        payment_id,
        current_user,
    )
