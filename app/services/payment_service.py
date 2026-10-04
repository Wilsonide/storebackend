import uuid
from datetime import datetime
from decimal import Decimal
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.integrations.paystack import paystack_client
from app.models.payment import Payment
from app.repositories.order_repository import order_repository
from app.repositories.payment_repository import (
    payment_repository,
)


class PaymentService:
    # ============================================================
    # INITIALIZE PAYMENT
    # ============================================================

    async def initialize_payment(
        self,
        session: AsyncSession,
        user,
        order_id: int,
    ) -> dict:
        order = await order_repository.get_by_id(
            session,
            order_id,
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        # --------------------------------------------------------
        # Ownership
        # --------------------------------------------------------

        if order.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot pay for this order.",
            )

        # --------------------------------------------------------
        # Check payment status
        # --------------------------------------------------------

        if order.payment_status == "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has already been paid for.",
            )

        # --------------------------------------------------------
        # Don't initialize cancelled orders
        # --------------------------------------------------------

        if order.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cancelled orders cannot be paid for.",
            )

        # --------------------------------------------------------
        # Existing payment
        # --------------------------------------------------------

        existing_payment = await payment_repository.get_by_order_id(
            session,
            order.id,
        )

        if existing_payment:
            if existing_payment.status == "successful":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order has already been paid for.",
                )

            # Return existing pending payment.
            return {
                "authorization_url": existing_payment.authorization_url,
                "access_code": existing_payment.access_code,
                "reference": existing_payment.reference,
            }

        # --------------------------------------------------------
        # Generate unique Paystack reference
        # --------------------------------------------------------

        reference = f"ORDER-{order.id}-{uuid.uuid4().hex[:12].upper()}"

        # --------------------------------------------------------
        # Convert Naira to Kobo
        # --------------------------------------------------------

        amount = int(Decimal(str(order.total_amount)) * 100)

        # --------------------------------------------------------
        # Paystack callback
        # --------------------------------------------------------

        callback_url = settings.PAYSTACK_CALLBACK_URL

        # --------------------------------------------------------
        # Initialize Paystack
        # --------------------------------------------------------

        paystack_data = await paystack_client.initialize_transaction(
            email=user.email,
            amount=amount,
            reference=reference,
            callback_url=callback_url,
        )

        # --------------------------------------------------------
        # Create payment record
        # --------------------------------------------------------

        payment = Payment(
            order_id=order.id,
            reference=reference,
            provider="paystack",
            status="pending",
            amount=order.total_amount,
            currency="NGN",
        )

        # --------------------------------------------------------
        # IMPORTANT:
        # If your Payment model has these fields, save them.
        # --------------------------------------------------------

        if hasattr(payment, "authorization_url"):
            payment.authorization_url = paystack_data["authorization_url"]

        if hasattr(payment, "access_code"):
            payment.access_code = paystack_data["access_code"]

        await payment_repository.create(
            session,
            payment,
        )

        return {
            "authorization_url": paystack_data["authorization_url"],
            "access_code": paystack_data["access_code"],
            "reference": paystack_data["reference"],
        }

    # ============================================================
    # VERIFY PAYMENT
    # ============================================================

    async def verify_payment(
        self,
        session: AsyncSession,
        reference: str,
    ) -> Payment:
        payment = await payment_repository.get_by_reference(
            session,
            reference,
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found.",
            )

        # --------------------------------------------------------
        # Already successful
        # --------------------------------------------------------

        if payment.status == "successful":
            return payment

        # --------------------------------------------------------
        # Ask Paystack
        # --------------------------------------------------------

        transaction = await paystack_client.verify_transaction(
            reference,
        )

        # --------------------------------------------------------
        # Verify reference
        # --------------------------------------------------------

        if transaction.get("reference") != reference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment reference mismatch.",
            )

        # --------------------------------------------------------
        # Verify currency
        # --------------------------------------------------------

        if transaction.get("currency") != payment.currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment currency mismatch.",
            )

        # --------------------------------------------------------
        # Verify amount
        # --------------------------------------------------------

        expected_amount = int(payment.amount * 100)

        paid_amount = transaction.get("amount")

        if paid_amount != expected_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment amount mismatch.",
            )

        # --------------------------------------------------------
        # Payment successful
        # --------------------------------------------------------

        if transaction.get("status") == "success":
            payment.status = "successful"

            payment.paid_at = datetime.utcnow()

            payment.order.payment_status = "paid"

            payment.order.status = "confirmed"

            await session.flush()

            return payment

        # --------------------------------------------------------
        # Payment failed
        # --------------------------------------------------------

        payment.status = "failed"

        await session.flush()

        return payment

    # ============================================================
    # GET PAYMENT
    # ============================================================

    async def get_payment(
        self,
        session: AsyncSession,
        payment_id: int,
        user,
    ) -> Payment:
        payment = await payment_repository.get_by_id(
            session,
            payment_id,
        )

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found.",
            )

        if payment.order.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )

        return payment

    # ============================================================
    # USER PAYMENTS
    # ============================================================

    async def get_user_payments(
        self,
        session: AsyncSession,
        user,
    ) -> list[Payment]:
        return await payment_repository.get_user_payments(
            session,
            user.id,
        )

    async def get_all_payments(
        self,
        session,
        current_user,
        page: int,
        page_size: int,
    ):
        # --------------------------------------------------------
        # ADMIN CHECK
        # --------------------------------------------------------

        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view payments.",
            )

        # --------------------------------------------------------
        # TOTAL
        # --------------------------------------------------------

        count_query = select(func.count(Payment.id))

        total_result = await session.execute(count_query)

        total = total_result.scalar_one()

        # --------------------------------------------------------
        # PAYMENTS
        # --------------------------------------------------------

        offset = (page - 1) * page_size

        query = (
            select(Payment)
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(query)

        payments = result.scalars().all()

        total_pages = ceil(total / page_size) if total else 0

        return {
            "items": payments,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }

    async def get_admin_payment(
        self,
        session,
        current_user,
        payment_id: int,
    ):
        # --------------------------------------------------------
        # ADMIN CHECK
        # --------------------------------------------------------

        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this payment.",
            )

        # --------------------------------------------------------
        # GET PAYMENT
        # --------------------------------------------------------

        query = select(Payment).where(Payment.id == payment_id)

        result = await session.execute(query)

        payment = result.scalar_one_or_none()

        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found.",
            )

        return payment


payment_service = PaymentService()
