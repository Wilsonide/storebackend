from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.repositories.order_repository import (
    order_repository,
)
from app.repositories.product_variant_repository import (
    product_variant_repository,
)


class OrderService:
    # ============================================================
    # CREATE ORDER
    # ============================================================

    async def create_order(
        self,
        session: AsyncSession,
        user,
        data,
    ) -> Order:
        total_amount = Decimal("0.00")

        order_items: list[OrderItem] = []

        variant_ids = [item.variant_id for item in data.items]

        # --------------------------------------------------------
        # Prevent duplicate variants
        # --------------------------------------------------------

        if len(variant_ids) != len(set(variant_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("A product variant can only appear once in an order."),
            )

        # --------------------------------------------------------
        # Validate variants
        # --------------------------------------------------------

        for item in data.items:
            variant = await product_variant_repository.get_by_id(
                session,
                item.variant_id,
            )

            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product variant not found.",
                )

            if not variant.is_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(f"Product variant {variant.sku} is unavailable."),
                )

            if variant.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient stock for "
                        f"{variant.sku}. "
                        f"Available quantity: "
                        f"{variant.quantity}."
                    ),
                )

            line_total = variant.price * item.quantity

            total_amount += line_total

            order_items.append(
                OrderItem(
                    variant_id=variant.id,
                    quantity=item.quantity,
                    price=variant.price,
                )
            )

        # --------------------------------------------------------
        # Create pending order
        # --------------------------------------------------------

        order = Order(
            total_amount=total_amount,
            status="pending",
            payment_status="unpaid",
            shipping_address=data.shipping_address,
            phone_number=data.phone_number,
            user_id=user.id,
            items=order_items,
        )

        return await order_repository.create(
            session,
            order,
        )

    # ============================================================
    # GET ORDER
    # ============================================================

    async def get_order(
        self,
        session: AsyncSession,
        order_id: int,
    ) -> Order:
        order = await order_repository.get_by_id(
            session,
            order_id,
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        return order

    # ============================================================
    # GET USER ORDER
    # ============================================================

    async def get_user_order(
        self,
        session: AsyncSession,
        order_id: int,
        user_id,
    ) -> Order:
        order = await order_repository.get_user_order(
            session,
            order_id,
            user_id,
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

        return order

    # ============================================================
    # GET ALL ORDERS
    # ============================================================

    async def get_orders(
        self,
        session: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        orders, total = await order_repository.get_all(
            session,
            page=page,
            page_size=page_size,
        )

        total_pages = (total + page_size - 1) // page_size

        return {
            "items": orders,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }

    # ============================================================
    # GET USER ORDERS
    # ============================================================

    async def get_user_orders(
        self,
        session: AsyncSession,
        user_id,
        *,
        page: int = 1,
        page_size: int = 20,
    ):
        orders, total = await order_repository.get_user_orders(
            session,
            user_id,
            page=page,
            page_size=page_size,
        )

        total_pages = (total + page_size - 1) // page_size

        return {
            "items": orders,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        }

    # ============================================================
    # FINALIZE INVENTORY
    # ============================================================

    async def finalize_inventory(
        self,
        session: AsyncSession,
        order: Order,
    ) -> None:
        for item in order.items:
            variant = await product_variant_repository.get_by_id_for_update(
                session,
                item.variant_id,
            )

            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(f"Variant {item.variant_id} not found."),
                )

            if variant.quantity < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(f"Insufficient stock for {variant.sku}."),
                )

            variant.quantity -= item.quantity

            if variant.quantity == 0:
                variant.is_available = False


order_service = OrderService()
