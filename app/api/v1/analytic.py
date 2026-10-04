from typing import Annotated

from fastapi import APIRouter, Query

from app.core.deps import DBSession
from app.schemas.analytic_service import (
    AnalyticsDashboardResponse,
    BestSellingProductResponse,
    RevenueResponse,
    SalesResponse,
    TotalItemsSoldResponse,
)
from app.services.analytic_service import analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ============================================================
# REVENUE
# ============================================================


@router.get(
    "/revenue",
    response_model=RevenueResponse,
)
async def revenue(
    session: DBSession,
):
    return {
        "revenue": await analytics_service.total_revenue(
            session,
        )
    }


# ============================================================
# SALES
# ============================================================


@router.get(
    "/sales",
    response_model=SalesResponse,
)
async def sales(
    session: DBSession,
):
    return {
        "sales": await analytics_service.total_sales(
            session,
        )
    }


# ============================================================
# TOTAL ITEMS SOLD
# ============================================================


@router.get(
    "/items-sold",
    response_model=TotalItemsSoldResponse,
)
async def total_items_sold(
    session: DBSession,
):
    return {
        "total_items_sold": (
            await analytics_service.total_items_sold(
                session,
            )
        )
    }


# ============================================================
# BEST SELLING PRODUCTS
# ============================================================


@router.get(
    "/best-products",
    response_model=list[BestSellingProductResponse],
)
async def best_products(
    session: DBSession,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
        ),
    ] = 10,
    offset: Annotated[
        int,
        Query(
            ge=0,
        ),
    ] = 0,
):
    return await analytics_service.best_selling_products(
        session,
        limit=limit,
        offset=offset,
    )


# ============================================================
# DASHBOARD
# ============================================================


@router.get(
    "/dashboard",
    response_model=AnalyticsDashboardResponse,
)
async def dashboard(
    session: DBSession,
):
    return await analytics_service.dashboard_summary(
        session,
    )
