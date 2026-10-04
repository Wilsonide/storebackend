from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.product_variant import ProductVariant


class ProductRepository:
    async def create(
        self,
        db: AsyncSession,
        product: Product,
    ) -> Product:
        db.add(product)

        await db.flush()

        await db.refresh(product)

        return product

    async def get_by_id(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> Product | None:
        result = await db.execute(
            select(Product)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images),
                selectinload(Product.category),
                selectinload(Product.brand),
            )
            .where(Product.id == product_id)
        )

        return result.scalar_one_or_none()

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

        # -----------------------------------
        # SEARCH
        # -----------------------------------

        if search:
            search_term = f"%{search.strip()}%"

            filters.append(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )

        # -----------------------------------
        # CATEGORY
        # -----------------------------------

        if category_id is not None:
            filters.append(Product.category_id == category_id)

        # -----------------------------------
        # BRAND
        # -----------------------------------

        if brand_id is not None:
            filters.append(Product.brand_id == brand_id)

        # -----------------------------------
        # FEATURED
        # -----------------------------------

        if featured is not None:
            filters.append(Product.is_featured == featured)

        # -----------------------------------
        # AVAILABILITY
        # -----------------------------------

        if available is not None:
            filters.append(Product.is_available == available)

        # -----------------------------------
        # PRICE FILTER
        #
        # Product price lives on ProductVariant
        # -----------------------------------

        if min_price is not None:
            filters.append(Product.variants.any(ProductVariant.price >= min_price))

        if max_price is not None:
            filters.append(Product.variants.any(ProductVariant.price <= max_price))

        # -----------------------------------
        # COUNT
        # -----------------------------------

        count_query = select(func.count(Product.id))

        if filters:
            count_query = count_query.where(*filters)

        count_result = await db.execute(count_query)

        total = count_result.scalar_one()

        # -----------------------------------
        # PRODUCT QUERY
        # -----------------------------------

        query = select(Product).options(
            selectinload(Product.variants),
        )

        if filters:
            query = query.where(*filters)

        # -----------------------------------
        # SORTING
        # -----------------------------------

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
                price_subquery.asc(),
                Product.id.desc(),
            )

        elif sort == "price_desc":
            price_subquery = (
                select(func.min(ProductVariant.price))
                .where(ProductVariant.product_id == Product.id)
                .scalar_subquery()
            )

            query = query.order_by(
                price_subquery.desc(),
                Product.id.desc(),
            )

        else:
            # newest

            query = query.order_by(
                Product.created_at.desc(),
                Product.id.desc(),
            )

        # -----------------------------------
        # PAGINATION
        # -----------------------------------

        offset = (page - 1) * page_size

        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)

        products = list(result.scalars().unique().all())

        return products, total

    async def search(
        self,
        db: AsyncSession,
        search_term: str,
    ) -> list[Product]:
        result = await db.execute(
            select(Product)
            .options(
                selectinload(Product.variants),
            )
            .where(Product.name.ilike(f"%{search_term}%"))
            .order_by(Product.name.asc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        product: Product,
        values: dict,
    ) -> Product:
        for field, value in values.items():
            setattr(
                product,
                field,
                value,
            )

        await db.flush()

        await db.refresh(product)

        return product

    async def delete(
        self,
        db: AsyncSession,
        product: Product,
    ) -> None:
        await db.delete(product)

        await db.flush()
