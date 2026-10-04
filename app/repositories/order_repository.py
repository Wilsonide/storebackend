from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product_variant import ProductVariant


class OrderRepository:
    async def create(
        self,
        session: AsyncSession,
        order: Order,
    ) -> Order:
        session.add(order)

        await session.flush()

        return order

    async def get_by_id(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> Order | None:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.product),
                selectinload(Order.payment),
            )
            .where(
                Order.id == order_id,
            )
        )

        result = await session.execute(stmt)

        return result.scalars().unique().one_or_none()

    async def get_user_order(
        self,
        session: AsyncSession,
        order_id: int,
        user_id,
    ) -> Order | None:
        stmt = (
            select(Order)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.product),
                selectinload(Order.payment),
            )
            .where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
        )

        result = await session.execute(stmt)

        return result.scalars().unique().one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        offset = (page - 1) * page_size

        count_stmt = select(func.count(Order.id))

        total_result = await session.execute(count_stmt)

        total = total_result.scalar_one()

        stmt = (
            select(Order)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.product),
                selectinload(Order.payment),
            )
            .order_by(
                Order.created_at.desc(),
            )
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(stmt)

        orders = list(result.scalars().unique().all())

        return orders, total

    async def get_user_orders(
        self,
        session: AsyncSession,
        user_id,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        offset = (page - 1) * page_size

        count_stmt = select(func.count(Order.id)).where(
            Order.user_id == user_id,
        )

        total_result = await session.execute(count_stmt)

        total = total_result.scalar_one()

        stmt = (
            select(Order)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.variant)
                .selectinload(ProductVariant.product),
                selectinload(Order.payment),
            )
            .where(
                Order.user_id == user_id,
            )
            .order_by(
                Order.created_at.desc(),
            )
            .offset(offset)
            .limit(page_size)
        )

        result = await session.execute(stmt)

        orders = list(result.scalars().unique().all())

        return orders, total


order_repository = OrderRepository()
