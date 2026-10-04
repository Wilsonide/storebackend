from fastapi import APIRouter

from app.api.v1.admin_orders import router as admin_orders_router
from app.api.v1.admin_payments import router as admin_payment_router
from app.api.v1.analytic import router as analytic_router
from app.api.v1.auth import router as auth_router
from app.api.v1.brands import router as brands_router
from app.api.v1.categories import router as categories_router
from app.api.v1.email_verify import router as email_verify_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.product_variants import (
    router as product_variants_router,
)
from app.api.v1.products import router as products_router

api_router = APIRouter()

api_router.include_router(
    brands_router,
)
api_router.include_router(
    analytic_router,
)
api_router.include_router(
    email_verify_router,
)
api_router.include_router(
    payments_router,
)
api_router.include_router(admin_payment_router)
api_router.include_router(
    auth_router,
)
api_router.include_router(
    admin_orders_router,
)
api_router.include_router(
    orders_router,
)

api_router.include_router(
    categories_router,
)

api_router.include_router(
    products_router,
)

api_router.include_router(
    product_variants_router,
)
