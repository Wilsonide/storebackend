from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import Brand
from app.repositories.brand_repository import BrandRepository
from app.schemas.brand import BrandCreate, BrandUpdate


class BrandService:
    def __init__(
        self,
        repository: BrandRepository,
    ):
        self.repository = repository

    async def create(
        self,
        db: AsyncSession,
        data: BrandCreate,
    ) -> Brand:
        existing = await self.repository.get_by_name(
            db,
            data.name,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Brand already exists.",
            )

        brand = Brand(
            name=data.name.strip(),
            description=data.description,
            image_url=data.image_url,
        )

        return await self.repository.create(
            db,
            brand,
        )

    async def get(
        self,
        db: AsyncSession,
        brand_id: int,
    ) -> Brand:
        brand = await self.repository.get_by_id(
            db,
            brand_id,
        )

        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found.",
            )

        return brand

    async def get_all(
        self,
        db: AsyncSession,
    ) -> list[Brand]:
        return await self.repository.get_all(db)

    async def update(
        self,
        db: AsyncSession,
        brand_id: int,
        data: BrandUpdate,
    ) -> Brand:
        brand = await self.get(
            db,
            brand_id,
        )

        values = data.model_dump(exclude_unset=True)

        if "name" in values:
            existing = await self.repository.get_by_name(
                db,
                values["name"],
            )

            if existing and existing.id != brand.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Brand already exists.",
                )

            values["name"] = values["name"].strip()

        return await self.repository.update(
            db,
            brand,
            values,
        )

    async def delete(
        self,
        db: AsyncSession,
        brand_id: int,
    ) -> None:
        brand = await self.get(
            db,
            brand_id,
        )

        await self.repository.delete(
            db,
            brand,
        )
