from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_variant import ProductVariant


class ProductVariantRepository:
    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        db: AsyncSession,
        variant: ProductVariant,
    ) -> ProductVariant:
        db.add(variant)

        await db.flush()
        await db.refresh(variant)

        return variant

    # ============================================================
    # GET BY ID
    # ============================================================

    async def get_by_id(
        self,
        db: AsyncSession,
        variant_id: int,
    ) -> ProductVariant | None:
        result = await db.execute(
            select(ProductVariant).where(
                ProductVariant.id == variant_id,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET BY ID WITH ROW LOCK
    #
    # Used during checkout/order creation.
    #
    # SELECT ... FOR UPDATE
    #
    # This prevents two customers from purchasing the same
    # inventory simultaneously.
    # ============================================================

    async def get_by_id_for_update(
        self,
        db: AsyncSession,
        variant_id: int,
    ) -> ProductVariant | None:
        result = await db.execute(
            select(ProductVariant)
            .where(
                ProductVariant.id == variant_id,
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()

    # ============================================================
    # GET BY SKU
    # ============================================================

    async def get_by_sku(
        self,
        db: AsyncSession,
        sku: str,
    ) -> ProductVariant | None:
        result = await db.execute(
            select(ProductVariant).where(
                ProductVariant.sku == sku,
            )
        )

        return result.scalar_one_or_none()

    # ============================================================
    # CHECK SKU EXISTS
    #
    # Useful when creating/updating variants.
    # ============================================================

    async def sku_exists(
        self,
        db: AsyncSession,
        sku: str,
        *,
        exclude_variant_id: int | None = None,
    ) -> bool:
        query = select(ProductVariant.id).where(
            ProductVariant.sku == sku,
        )

        if exclude_variant_id is not None:
            query = query.where(
                ProductVariant.id != exclude_variant_id,
            )

        result = await db.execute(query)

        return result.scalar_one_or_none() is not None

    # ============================================================
    # GET PRODUCT VARIANTS
    # ============================================================

    async def get_product_variants(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> list[ProductVariant]:
        result = await db.execute(
            select(ProductVariant)
            .where(
                ProductVariant.product_id == product_id,
            )
            .order_by(
                ProductVariant.is_default.desc(),
                ProductVariant.id.asc(),
            )
        )

        return list(result.scalars().all())

    # ============================================================
    # UPDATE
    # ============================================================

    async def update(
        self,
        db: AsyncSession,
        variant: ProductVariant,
        values: dict,
    ) -> ProductVariant:
        for field, value in values.items():
            setattr(
                variant,
                field,
                value,
            )

        await db.flush()
        await db.refresh(variant)

        return variant

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        db: AsyncSession,
        variant: ProductVariant,
    ) -> None:
        await db.delete(variant)

        await db.flush()


product_variant_repository = ProductVariantRepository()
