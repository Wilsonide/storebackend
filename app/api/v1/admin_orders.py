from typing import Annotated

from fastapi import APIRouter, Query

from app.core.deps import DBSession
from app.services.order_service import order_service

router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Orders"],
)


@router.get("")
async def get_orders(
    session: DBSession,
    page: Annotated[
        int,
        Query(ge=1),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
):
    return await order_service.get_orders(
        session,
        page=page,
        page_size=page_size,
    )


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    session: DBSession,
):
    return await order_service.get_order(
        session,
        order_id,
    )
