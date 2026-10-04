from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class PaystackClient:
    def __init__(self):
        self.base_url = settings.PAYSTACK_BASE_URL

        self.headers = {
            "Authorization": (f"Bearer {settings.PAYSTACK_SECRET_KEY}"),
            "Content-Type": "application/json",
        }

    async def initialize_transaction(
        self,
        *,
        email: str,
        amount: int,
        reference: str,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "email": email,
            "amount": amount,
            "reference": reference,
            "currency": settings.PAYSTACK_CURRENCY,
        }

        if callback_url:
            payload["callback_url"] = callback_url

        try:
            async with httpx.AsyncClient(
                timeout=30.0,
            ) as client:
                response = await client.post(
                    f"{self.base_url}/transaction/initialize",
                    headers=self.headers,
                    json=payload,
                )

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to connect to Paystack.",
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Paystack payment initialization failed.",
            )

        data = response.json()

        if not data.get("status"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=data.get(
                    "message",
                    "Paystack payment initialization failed.",
                ),
            )

        return data["data"]

    async def verify_transaction(
        self,
        reference: str,
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
            ) as client:
                response = await client.get(
                    (f"{self.base_url}/transaction/verify/{reference}"),
                    headers=self.headers,
                )

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to connect to Paystack.",
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Paystack payment verification failed.",
            )

        data = response.json()

        if not data.get("status"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=data.get(
                    "message",
                    "Payment verification failed.",
                ),
            )

        return data["data"]


paystack_client = PaystackClient()
