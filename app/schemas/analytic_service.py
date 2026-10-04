from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BestSellingProductResponse(BaseModel):
    product_id: int
    product_name: str
    cover_image: str | None
    total_sold: int


class AnalyticsDashboardResponse(BaseModel):
    total_revenue: Decimal
    total_sales: int
    total_items_sold: int

    best_selling_products: list[BestSellingProductResponse]


class RevenueResponse(BaseModel):
    revenue: Decimal


class SalesResponse(BaseModel):
    sales: int


class TotalItemsSoldResponse(BaseModel):
    total_items_sold: int
