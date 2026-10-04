from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_variant import ProductVariant
from app.repositories.product_repository import ProductRepository
from app.repositories.product_variant_repository import (
    ProductVariantRepository,
)
from app.schemas.product_variant import (
    ProductVariantCreate,
    ProductVariantUpdate,
)


class ProductVariantService:
    def __init__(
        self,
        repository: ProductVariantRepository,
        product_repository: ProductRepository,
    ):
        self.repository = repository
        self.product_repository = product_repository

    async def create(
        self,
        db: AsyncSession,
        product_id: int,
        data: ProductVariantCreate,
    ) -> ProductVariant:
        product = await self.product_repository.get_by_id(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        existing = await self.repository.get_by_sku(
            db,
            data.sku,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU already exists.",
            )

        if data.is_default:
            await self._remove_default_variant(
                db,
                product_id,
            )

        variant = ProductVariant(
            product_id=product_id,
            sku=data.sku.strip(),
            price=data.price,
            quantity=data.quantity,
            color=data.color,
            size=data.size,
            material=data.material,
            style=data.style,
            strap_type=data.strap_type,
            is_default=data.is_default,
            is_available=data.is_available,
        )

        return await self.repository.create(
            db,
            variant,
        )

    async def get(
        self,
        db: AsyncSession,
        variant_id: int,
    ) -> ProductVariant:
        variant = await self.repository.get_by_id(
            db,
            variant_id,
        )

        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variant not found.",
            )

        return variant

    async def get_product_variants(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> list[ProductVariant]:
        product = await self.product_repository.get_by_id(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return await self.repository.get_product_variants(
            db,
            product_id,
        )

    async def update(
        self,
        db: AsyncSession,
        variant_id: int,
        data: ProductVariantUpdate,
    ) -> ProductVariant:
        variant = await self.get(
            db,
            variant_id,
        )

        values = data.model_dump(exclude_unset=True)

        if "sku" in values:
            existing = await self.repository.get_by_sku(
                db,
                values["sku"],
            )

            if existing and existing.id != variant.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="SKU already exists.",
                )

            values["sku"] = values["sku"].strip()

        if values.get("is_default") is True:
            await self._remove_default_variant(
                db,
                variant.product_id,
            )

        return await self.repository.update(
            db,
            variant,
            values,
        )

    async def delete(
        self,
        db: AsyncSession,
        variant_id: int,
    ) -> None:
        variant = await self.get(
            db,
            variant_id,
        )

        await self.repository.delete(
            db,
            variant,
        )

    async def _remove_default_variant(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> None:
        variants = await self.repository.get_product_variants(
            db,
            product_id,
        )

        for variant in variants:
            if variant.is_default:
                variant.is_default = False

        await db.flush()
