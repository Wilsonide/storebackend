from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.db.database import get_db
from app.schemas.order import (
    OrderCreate,
    OrderListResponse,
    OrderResponse,
)
from app.services.order_service import order_service

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


# ============================================================
# CREATE ORDER
# ============================================================


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    data: OrderCreate,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: CurrentUser,
):
    order = await order_service.create_order(
        session,
        user,
        data,
    )

    await session.commit()

    return await order_service.get_order(
        session,
        order.id,
    )


# ============================================================
# MY ORDERS
# ============================================================


@router.get(
    "/me",
    response_model=OrderListResponse,
)
async def get_my_orders(
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await order_service.get_user_orders(
        session,
        user.id,
        page=page,
        page_size=page_size,
    )


# ============================================================
# MY SINGLE ORDER
# ============================================================


@router.get(
    "/me/{order_id}",
    response_model=OrderResponse,
)
async def get_my_order(
    order_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: CurrentUser,
):
    return await order_service.get_user_order(
        session,
        order_id,
        user.id,
    )
