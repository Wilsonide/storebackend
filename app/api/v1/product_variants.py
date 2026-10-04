from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.product import (
    get_product_variant_service,
)
from app.db.database import get_db
from app.schemas.product_variant import (
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)
from app.services.product_variant_service import (
    ProductVariantService,
)

router = APIRouter(
    prefix="/products",
    tags=["Product Variants"],
)


@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_variant(
    product_id: int,
    data: ProductVariantCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ProductVariantService, Depends(get_product_variant_service)],
):
    variant = await service.create(
        db,
        product_id,
        data,
    )

    await db.commit()

    return variant


@router.get(
    "/{product_id}/variants",
    response_model=list[ProductVariantResponse],
)
async def get_product_variants(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ProductVariantService, Depends(get_product_variant_service)],
):
    return await service.get_product_variants(
        db,
        product_id,
    )


@router.get(
    "/variants/{variant_id}",
    response_model=ProductVariantResponse,
)
async def get_product_variant(
    variant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ProductVariantService, Depends(get_product_variant_service)],
):
    return await service.get(
        db,
        variant_id,
    )


@router.patch(
    "/variants/{variant_id}",
    response_model=ProductVariantResponse,
)
async def update_product_variant(
    variant_id: int,
    data: ProductVariantUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ProductVariantService, Depends(get_product_variant_service)],
):
    variant = await service.update(
        db,
        variant_id,
        data,
    )

    await db.commit()

    return variant


@router.delete(
    "/variants/{variant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product_variant(
    variant_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ProductVariantService, Depends(get_product_variant_service)],
):
    await service.delete(
        db,
        variant_id,
    )

    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
