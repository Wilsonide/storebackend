from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    async def create(
        self,
        db: AsyncSession,
        category: Category,
    ) -> Category:
        db.add(category)

        await db.flush()
        await db.refresh(category)

        return category

    async def get_by_id(
        self,
        db: AsyncSession,
        category_id: int,
    ) -> Category | None:
        result = await db.execute(select(Category).where(Category.id == category_id))

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Category | None:
        result = await db.execute(select(Category).where(Category.name.ilike(name)))

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
    ) -> list[Category]:
        result = await db.execute(select(Category).order_by(Category.name.asc()))

        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        category: Category,
        values: dict,
    ) -> Category:
        for field, value in values.items():
            setattr(category, field, value)

        await db.flush()
        await db.refresh(category)

        return category

    async def delete(
        self,
        db: AsyncSession,
        category: Category,
    ) -> None:
        await db.delete(category)
        await db.flush()
