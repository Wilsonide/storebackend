from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.payment import Payment


class PaymentRepository:
    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        session: AsyncSession,
        payment: Payment,
    ) -> Payment:
        session.add(payment)

        await session.flush()

        await session.refresh(payment)

        return payment

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        session: AsyncSession,
        payment_id: int,
    ) -> Payment | None:
        stmt = (
            select(Payment)
            .options(
                selectinload(
                    Payment.order,
                ),
            )
            .where(
                Payment.id == payment_id,
            )
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    # ============================================================
    # GET BY REFERENCE
    # ============================================================

    async def get_by_reference(
        self,
        session: AsyncSession,
        reference: str,
    ) -> Payment | None:
        stmt = (
            select(Payment)
            .options(
                selectinload(
                    Payment.order,
                ),
            )
            .where(
                Payment.reference == reference,
            )
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    # ============================================================
    # GET BY ORDER
    # ============================================================

    async def get_by_order_id(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> Payment | None:
        stmt = select(Payment).where(
            Payment.order_id == order_id,
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    # ============================================================
    # GET USER PAYMENTS
    # ============================================================

    async def get_user_payments(
        self,
        session: AsyncSession,
        user_id,
    ) -> list[Payment]:
        stmt = (
            select(Payment)
            .join(Order)
            .where(
                Order.user_id == user_id,
            )
            .order_by(
                Payment.created_at.desc(),
            )
        )

        result = await session.execute(stmt)

        return list(result.scalars().all())


payment_repository = PaymentRepository()
