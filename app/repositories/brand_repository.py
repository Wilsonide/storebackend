from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand


class BrandRepository:
    async def create(
        self,
        db: AsyncSession,
        brand: Brand,
    ) -> Brand:
        db.add(brand)

        await db.flush()
        await db.refresh(brand)

        return brand

    async def get_by_id(
        self,
        db: AsyncSession,
        brand_id: int,
    ) -> Brand | None:
        result = await db.execute(select(Brand).where(Brand.id == brand_id))

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Brand | None:
        result = await db.execute(select(Brand).where(Brand.name.ilike(name)))

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
    ) -> list[Brand]:
        result = await db.execute(select(Brand).order_by(Brand.name.asc()))

        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        brand: Brand,
        values: dict,
    ) -> Brand:
        for field, value in values.items():
            setattr(brand, field, value)

        await db.flush()
        await db.refresh(brand)

        return brand

    async def delete(
        self,
        db: AsyncSession,
        brand: Brand,
    ) -> None:
        await db.delete(brand)
        await db.flush()
