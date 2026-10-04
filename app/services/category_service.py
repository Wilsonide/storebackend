from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(
        self,
        repository: CategoryRepository,
    ):
        self.repository = repository

    async def create(
        self,
        db: AsyncSession,
        data: CategoryCreate,
    ) -> Category:
        existing = await self.repository.get_by_name(
            db,
            data.name,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists.",
            )

        category = Category(
            name=data.name.strip(),
        )

        return await self.repository.create(
            db,
            category,
        )

    async def get(
        self,
        db: AsyncSession,
        category_id: int,
    ) -> Category:
        category = await self.repository.get_by_id(
            db,
            category_id,
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        return category

    async def get_all(
        self,
        db: AsyncSession,
    ) -> list[Category]:
        return await self.repository.get_all(db)

    async def update(
        self,
        db: AsyncSession,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category:
        category = await self.get(
            db,
            category_id,
        )

        values = data.model_dump(exclude_unset=True)

        if "name" in values:
            existing = await self.repository.get_by_name(
                db,
                values["name"],
            )

            if existing and existing.id != category.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Category already exists.",
                )

            values["name"] = values["name"].strip()

        return await self.repository.update(
            db,
            category,
            values,
        )

    async def delete(
        self,
        db: AsyncSession,
        category_id: int,
    ) -> None:
        category = await self.get(
            db,
            category_id,
        )

        await self.repository.delete(
            db,
            category,
        )
