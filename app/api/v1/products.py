from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.product import get_product_service
from app.db.database import get_db
from app.schemas.product import (
    PaginatedProductResponse,
    ProductCreate,
    ProductListResponse,
    ProductQueryParams,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# ============================================================
# CREATE PRODUCT
# ============================================================


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
):
    product = await service.create(
        db,
        data,
    )

    await db.commit()

    return await service.get(
        db,
        product.id,
    )


# ============================================================
# GET PRODUCTS
#
# Supports:
# - pagination
# - search
# - category
# - brand
# - featured
# - availability
# - min/max price
# - sorting
# ============================================================


@router.get(
    "",
    response_model=PaginatedProductResponse,
)
async def get_products(
    params: Annotated[
        ProductQueryParams,
        Depends(),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
):
    return await service.get_paginated(
        db,
        params,
    )


# ============================================================
# SEARCH PRODUCTS
#
# Kept for backwards compatibility.
#
# Example:
# GET /products/search?q=gold
# ============================================================


@router.get(
    "/search",
    response_model=list[ProductListResponse],
)
async def search_products(
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
    q: Annotated[
        str,
        Query(
            min_length=1,
            max_length=100,
        ),
    ],
):
    return await service.search(
        db,
        q,
    )


# ============================================================
# GET SINGLE PRODUCT
# ============================================================


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
async def get_product(
    product_id: int,
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
):
    return await service.get(
        db,
        product_id,
    )


# ============================================================
# UPDATE PRODUCT
# ============================================================


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
):
    await service.update(
        db,
        product_id,
        data,
    )

    await db.commit()

    return await service.get(
        db,
        product_id,
    )


# ============================================================
# DELETE PRODUCT
# ============================================================


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: int,
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    service: Annotated[
        ProductService,
        Depends(get_product_service),
    ],
):
    await service.delete(
        db,
        product_id,
    )

    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
