from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.repositories.brand_repository import BrandRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    PaginatedProductResponse,
    ProductCreate,
    ProductQueryParams,
    ProductUpdate,
)


class ProductService:
    def __init__(
        self,
        repository: ProductRepository,
        category_repository: CategoryRepository,
        brand_repository: BrandRepository,
    ):
        self.repository = repository
        self.category_repository = category_repository
        self.brand_repository = brand_repository

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        db: AsyncSession,
        data: ProductCreate,
    ) -> Product:
        # --------------------------------------------------------
        # Validate category
        # --------------------------------------------------------

        category = await self.category_repository.get_by_id(
            db,
            data.category_id,
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        # --------------------------------------------------------
        # Validate brand
        # --------------------------------------------------------

        if data.brand_id is not None:
            brand = await self.brand_repository.get_by_id(
                db,
                data.brand_id,
            )

            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brand not found.",
                )

        # --------------------------------------------------------
        # Product must have at least one variant
        # --------------------------------------------------------

        if not data.variants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A product must have at least one variant.",
            )

        # --------------------------------------------------------
        # Validate default variants
        # --------------------------------------------------------

        default_variants = [variant for variant in data.variants if variant.is_default]

        if len(default_variants) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A product can have only one default variant.",
            )

        # --------------------------------------------------------
        # Create product
        # --------------------------------------------------------

        product = Product(
            name=data.name.strip(),
            description=data.description.strip(),
            category_id=data.category_id,
            brand_id=data.brand_id,
            material=(data.material.strip() if data.material else None),
            gender=(data.gender.strip() if data.gender else None),
            warranty=(data.warranty.strip() if data.warranty else None),
            cover_image=data.cover_image,
            cover_public_id=data.cover_public_id,
            is_available=data.is_available,
            is_featured=data.is_featured,
        )

        # --------------------------------------------------------
        # Create variants
        # --------------------------------------------------------

        for variant_data in data.variants:
            variant = ProductVariant(
                price=variant_data.price,
                quantity=variant_data.quantity,
                color=(variant_data.color.strip() if variant_data.color else None),
                size=(variant_data.size.strip() if variant_data.size else None),
                is_default=variant_data.is_default,
                is_available=variant_data.is_available,
            )

            product.variants.append(variant)

        # --------------------------------------------------------
        # Persist
        # --------------------------------------------------------

        return await self.repository.create(
            db,
            product,
        )

    # ============================================================
    # GET SINGLE PRODUCT
    # ============================================================

    async def get(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> Product:
        product = await self.repository.get_by_id(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return product

    # ============================================================
    # GET PAGINATED PRODUCTS
    # ============================================================

    async def get_paginated(
        self,
        db: AsyncSession,
        params: ProductQueryParams,
    ) -> PaginatedProductResponse:
        # --------------------------------------------------------
        # Validate price range
        # --------------------------------------------------------

        if (
            params.min_price is not None
            and params.max_price is not None
            and params.min_price > params.max_price
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price.",
            )

        # --------------------------------------------------------
        # Normalize search
        # --------------------------------------------------------

        search = params.search.strip() if params.search else None

        # --------------------------------------------------------
        # Repository
        # --------------------------------------------------------

        products, total = await self.repository.get_paginated(
            db,
            page=params.page,
            page_size=params.page_size,
            search=search,
            category_id=params.category_id,
            brand_id=params.brand_id,
            featured=params.featured,
            available=params.available,
            min_price=params.min_price,
            max_price=params.max_price,
            sort=params.sort,
        )

        # --------------------------------------------------------
        # Calculate pagination metadata
        # --------------------------------------------------------

        total_pages = (
            (total + params.page_size - 1) // params.page_size if total > 0 else 0
        )

        has_next = params.page < total_pages

        has_previous = params.page > 1

        # --------------------------------------------------------
        # Return paginated response
        # --------------------------------------------------------

        return PaginatedProductResponse(
            items=products,
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous,
        )

    # ============================================================
    # GET ALL PRODUCTS
    #
    # Keep this for backwards compatibility with existing code.
    # New storefront listing should use get_paginated().
    # ============================================================

    async def get_all(
        self,
        db: AsyncSession,
        *,
        category_id: int | None = None,
        brand_id: int | None = None,
        featured: bool | None = None,
        available: bool | None = None,
    ) -> list[Product]:
        return await self.repository.get_all(
            db,
            category_id=category_id,
            brand_id=brand_id,
            featured=featured,
            available=available,
        )

    # ============================================================
    # SEARCH
    #
    # Keep this for backwards compatibility.
    # New product listing should preferably use get_paginated()
    # with the search parameter.
    # ============================================================

    async def search(
        self,
        db: AsyncSession,
        search_term: str,
    ) -> list[Product]:
        search_term = search_term.strip()

        if not search_term:
            return []

        return await self.repository.search(
            db,
            search_term,
        )

    # ============================================================
    # UPDATE
    # ============================================================

    async def update(
        self,
        db: AsyncSession,
        product_id: int,
        data: ProductUpdate,
    ) -> Product:
        # --------------------------------------------------------
        # Get existing product
        # --------------------------------------------------------

        product = await self.get(
            db,
            product_id,
        )

        # --------------------------------------------------------
        # Extract only supplied fields
        # --------------------------------------------------------

        values = data.model_dump(
            exclude_unset=True,
        )

        if not values:
            return product

        # --------------------------------------------------------
        # Validate category if being changed
        # --------------------------------------------------------

        if "category_id" in values:
            category = await self.category_repository.get_by_id(
                db,
                values["category_id"],
            )

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found.",
                )

        # --------------------------------------------------------
        # Validate brand if being changed
        # --------------------------------------------------------

        if "brand_id" in values:
            if values["brand_id"] is not None:
                brand = await self.brand_repository.get_by_id(
                    db,
                    values["brand_id"],
                )

                if not brand:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Brand not found.",
                    )

        # --------------------------------------------------------
        # Normalize strings
        # --------------------------------------------------------

        string_fields = [
            "name",
            "description",
            "material",
            "gender",
            "warranty",
        ]

        for field in string_fields:
            if field in values and values[field] is not None:
                values[field] = values[field].strip()

        # --------------------------------------------------------
        # Update
        # --------------------------------------------------------

        return await self.repository.update(
            db,
            product,
            values,
        )

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> None:
        # --------------------------------------------------------
        # Get existing product
        # --------------------------------------------------------

        product = await self.get(
            db,
            product_id,
        )

        # --------------------------------------------------------
        # Delete
        # --------------------------------------------------------

        await self.repository.delete(
            db,
            product,
        )
