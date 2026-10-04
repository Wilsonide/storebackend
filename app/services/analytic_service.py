from datetime import datetime
from decimal import Decimal

from app.repositories.analytic_repository import (
    analytics_repository,
)


class AnalyticsService:
    # ============================================================
    # TOTAL REVENUE
    # ============================================================

    async def total_revenue(
        self,
        session,
    ) -> Decimal:
        return await analytics_repository.get_total_revenue(
            session,
        )

    # ============================================================
    # TOTAL SALES
    # ============================================================

    async def total_sales(
        self,
        session,
    ) -> int:
        return await analytics_repository.get_total_sales(
            session,
        )

    # ============================================================
    # TOTAL ITEMS SOLD
    # ============================================================

    async def total_items_sold(
        self,
        session,
    ) -> int:
        return await analytics_repository.get_total_items_sold(
            session,
        )

    # ============================================================
    # BEST SELLING PRODUCTS
    # ============================================================

    async def best_selling_products(
        self,
        session,
        *,
        limit: int = 10,
        offset: int = 0,
    ):
        rows = await analytics_repository.get_best_selling_products(
            session,
            limit=limit,
            offset=offset,
        )

        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "cover_image": row.cover_image,
                "total_sold": row.total_sold,
            }
            for row in rows
        ]

    # ============================================================
    # DASHBOARD SUMMARY
    # ============================================================

    async def dashboard_summary(
        self,
        session,
    ):
        revenue = await self.total_revenue(
            session,
        )

        sales = await self.total_sales(
            session,
        )

        items_sold = await self.total_items_sold(
            session,
        )

        best_products = await self.best_selling_products(
            session,
            limit=10,
            offset=0,
        )

        return {
            "total_revenue": revenue,
            "total_sales": sales,
            "total_items_sold": items_sold,
            "best_selling_products": best_products,
        }


analytics_service = AnalyticsService()
