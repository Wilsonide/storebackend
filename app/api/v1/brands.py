from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.product import get_brand_service
from app.db.database import get_db
from app.schemas.brand import (
    BrandCreate,
    BrandResponse,
    BrandUpdate,
)
from app.services.brand_service import BrandService

router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
)


@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_brand(
    data: BrandCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[BrandService, Depends(get_brand_service)],
):
    brand = await service.create(
        db,
        data,
    )

    await db.commit()

    return brand


@router.get(
    "",
    response_model=list[BrandResponse],
)
async def get_brands(
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[BrandService, Depends(get_brand_service)],
):
    return await service.get_all(db)


@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
)
async def get_brand(
    service: Annotated[BrandService, Depends(get_brand_service)],
    brand_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await service.get(
        db,
        brand_id,
    )


@router.patch(
    "/{brand_id}",
    response_model=BrandResponse,
)
async def update_brand(
    brand_id: int,
    data: BrandUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[BrandService, Depends(get_brand_service)],
):
    brand = await service.update(
        db,
        brand_id,
        data,
    )

    await db.commit()

    return brand


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_brand(
    brand_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[BrandService, Depends(get_brand_service)],
):
    await service.delete(
        db,
        brand_id,
    )

    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
