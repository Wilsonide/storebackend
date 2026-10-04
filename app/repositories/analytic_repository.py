from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.product_variant import ProductVariant


class AnalyticsRepository:
    # ============================================================
    # TOTAL REVENUE
    # ============================================================

    async def get_total_revenue(
        self,
        session: AsyncSession,
    ):
        stmt = select(
            func.coalesce(
                func.sum(Order.total_amount),
                0,
            )
        ).where(
            Order.payment_status == "paid",
        )

        result = await session.execute(stmt)

        return result.scalar_one()

    # ============================================================
    # TOTAL SALES
    #
    # Number of paid orders.
    # ============================================================

    async def get_total_sales(
        self,
        session: AsyncSession,
    ) -> int:
        stmt = select(func.count(Order.id)).where(
            Order.payment_status == "paid",
        )

        result = await session.execute(stmt)

        return result.scalar_one()

    # ============================================================
    # TOTAL ITEMS SOLD
    # ============================================================

    async def get_total_items_sold(
        self,
        session: AsyncSession,
    ) -> int:
        stmt = (
            select(
                func.coalesce(
                    func.sum(OrderItem.quantity),
                    0,
                )
            )
            .join(
                Order,
                Order.id == OrderItem.order_id,
            )
            .where(
                Order.payment_status == "paid",
            )
        )

        result = await session.execute(stmt)

        return result.scalar_one()

    # ============================================================
    # BEST SELLING PRODUCTS
    #
    # Groups sales by Product.
    # ============================================================

    async def get_best_selling_products(
        self,
        session: AsyncSession,
        *,
        limit: int = 10,
        offset: int = 0,
    ):
        total_sold = func.sum(OrderItem.quantity).label("total_sold")

        stmt = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.cover_image.label("cover_image"),
                total_sold,
            )
            .join(
                ProductVariant,
                ProductVariant.product_id == Product.id,
            )
            .join(
                OrderItem,
                OrderItem.variant_id == ProductVariant.id,
            )
            .join(
                Order,
                Order.id == OrderItem.order_id,
            )
            .where(
                Order.payment_status == "paid",
            )
            .group_by(
                Product.id,
                Product.name,
                Product.cover_image,
            )
            .order_by(
                total_sold.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(stmt)

        return result.all()

    # ============================================================
    # REVENUE BY DATE RANGE
    # ============================================================

    async def get_revenue_by_date_range(
        self,
        session: AsyncSession,
        *,
        start_date: datetime,
        end_date: datetime,
    ):
        stmt = select(
            func.coalesce(
                func.sum(Order.total_amount),
                0,
            )
        ).where(
            Order.payment_status == "paid",
            Order.created_at >= start_date,
            Order.created_at < end_date,
        )

        result = await session.execute(stmt)

        return result.scalar_one()

    # ============================================================
    # SALES BY DATE RANGE
    # ============================================================

    async def get_sales_by_date_range(
        self,
        session: AsyncSession,
        *,
        start_date: datetime,
        end_date: datetime,
    ) -> int:
        stmt = select(func.count(Order.id)).where(
            Order.payment_status == "paid",
            Order.created_at >= start_date,
            Order.created_at < end_date,
        )

        result = await session.execute(stmt)

        return result.scalar_one()


analytics_repository = AnalyticsRepository()
