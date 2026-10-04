from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.product import get_category_service
from app.db.database import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    category = await service.create(
        db,
        data,
    )

    await db.commit()

    return category


@router.get(
    "",
    response_model=list[CategoryResponse],
)
async def get_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    return await service.get_all(db)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
async def get_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    return await service.get(
        db,
        category_id,
    )


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    category = await service.update(
        db,
        category_id,
        data,
    )

    await db.commit()

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[CategoryService, Depends(get_category_service)],
):
    await service.delete(
        db,
        category_id,
    )

    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
