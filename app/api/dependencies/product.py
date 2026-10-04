from app.repositories.brand_repository import BrandRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.product_variant_repository import (
    ProductVariantRepository,
)
from app.services.brand_service import BrandService
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.services.product_variant_service import ProductVariantService


def get_brand_service() -> BrandService:
    return BrandService(
        repository=BrandRepository(),
    )


def get_category_service() -> CategoryService:
    return CategoryService(
        repository=CategoryRepository(),
    )


def get_product_service() -> ProductService:
    return ProductService(
        repository=ProductRepository(),
        category_repository=CategoryRepository(),
        brand_repository=BrandRepository(),
    )


def get_product_variant_service() -> ProductVariantService:
    return ProductVariantService(
        repository=ProductVariantRepository(),
        product_repository=ProductRepository(),
    )
