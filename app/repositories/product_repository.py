from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.product_variant import ProductVariant


class ProductRepository:
    """Database operations for products and their related records."""

    @staticmethod
    def _product_options():
        """Eager-load relationships used by product responses."""
        return (
            selectinload(Product.variants),
            selectinload(Product.images),
            selectinload(Product.category),
            selectinload(Product.brand),
        )

    async def create(
        self,
        db: AsyncSession,
        product: Product,
    ) -> Product:
        db.add(product)
        await db.flush()

        # Reload with relationships so the service/controller can safely
        # serialize variants, images, category, and brand.
        return await self._get_product_or_none(db, product.id) or product

    async def _get_product_or_none(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> Product | None:
        result = await db.execute(
            select(Product)
            .options(*self._product_options())
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> Product | None:
        return await self._get_product_or_none(db, product_id)

    async def get_paginated(
        self,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        category_id: int | None = None,
        brand_id: int | None = None,
        featured: bool | None = None,
        available: bool | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort: str = "newest",
    ) -> tuple[list[Product], int]:
        filters = []

        # Search product names and descriptions.
        if search:
            search_term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )

        if category_id is not None:
            filters.append(Product.category_id == category_id)

        if brand_id is not None:
            filters.append(Product.brand_id == brand_id)

        if featured is not None:
            filters.append(Product.is_featured == featured)

        if available is not None:
            filters.append(Product.is_available == available)

        # Product prices are stored on ProductVariant.
        if min_price is not None:
            filters.append(
                Product.variants.any(ProductVariant.price >= min_price)
            )

        if max_price is not None:
            filters.append(
                Product.variants.any(ProductVariant.price <= max_price)
            )

        # Count matching products before pagination.
        count_query = select(func.count(Product.id))
        if filters:
            count_query = count_query.where(*filters)

        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        # Load images and variants for every product in the result.
        query = select(Product).options(*self._product_options())

        if filters:
            query = query.where(*filters)

        # Sorting.
        if sort == "oldest":
            query = query.order_by(
                Product.created_at.asc(),
                Product.id.asc(),
            )

        elif sort == "name_asc":
            query = query.order_by(
                Product.name.asc(),
                Product.id.asc(),
            )

        elif sort == "name_desc":
            query = query.order_by(
                Product.name.desc(),
                Product.id.desc(),
            )

        elif sort == "price_asc":
            price_subquery = (
                select(func.min(ProductVariant.price))
                .where(ProductVariant.product_id == Product.id)
                .scalar_subquery()
            )
            query = query.order_by(
                price_subquery.asc().nulls_last(),
                Product.id.desc(),
            )

        elif sort == "price_desc":
            # Sort by the highest variant price, descending.
            price_subquery = (
                select(func.max(ProductVariant.price))
                .where(ProductVariant.product_id == Product.id)
                .scalar_subquery()
            )
            query = query.order_by(
                price_subquery.desc().nulls_last(),
                Product.id.desc(),
            )

        else:
            # Default: newest products first.
            query = query.order_by(
                Product.created_at.desc(),
                Product.id.desc(),
            )

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        products = list(result.scalars().unique().all())

        return products, total

    async def get_all(
        self,
        db: AsyncSession,
        *,
        category_id: int | None = None,
        brand_id: int | None = None,
        featured: bool | None = None,
        available: bool | None = None,
    ) -> list[Product]:
        query = select(Product).options(*self._product_options())

        if category_id is not None:
            query = query.where(Product.category_id == category_id)

        if brand_id is not None:
            query = query.where(Product.brand_id == brand_id)

        if featured is not None:
            query = query.where(Product.is_featured == featured)

        if available is not None:
            query = query.where(Product.is_available == available)

        query = query.order_by(
            Product.created_at.desc(),
            Product.id.desc(),
        )

        result = await db.execute(query)
        return list(result.scalars().unique().all())

    async def search(
        self,
        db: AsyncSession,
        search_term: str,
    ) -> list[Product]:
        search_term = search_term.strip()

        if not search_term:
            return []

        pattern = f"%{search_term}%"

        result = await db.execute(
            select(Product)
            .options(*self._product_options())
            .where(
                or_(
                    Product.name.ilike(pattern),
                    Product.description.ilike(pattern),
                )
            )
            .order_by(Product.name.asc(), Product.id.asc())
        )

        return list(result.scalars().unique().all())

    async def update(
        self,
        db: AsyncSession,
        product: Product,
        values: dict,
    ) -> Product:
        for field, value in values.items():
            setattr(product, field, value)

        await db.flush()

        # Re-query with eager-loaded relationships for reliable serialization.
        return await self._get_product_or_none(db, product.id) or product

    async def delete(
        self,
        db: AsyncSession,
        product: Product,
    ) -> None:
        await db.delete(product)
        await db.flush()