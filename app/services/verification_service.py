from datetime import UTC, datetime
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import DBSession
from app.models.email_verification import EmailVerification
from app.repositories.verification_repository import EmailVerificationRepository
from app.services.user_service import user_service
from app.utils.helper import (
    generate_verification_token,
    hash_verification_token,
    verification_token_expiry,
)


class EmailVerificationService:
    def __init__(self):
        self.repo = EmailVerificationRepository()

    async def create(
        self,
        session: DBSession,
        current_user_id,
    ) -> str:
        current_user = await user_service.get_user_by_id(session, current_user_id)

        raw_token = generate_verification_token()
        token_hash = hash_verification_token(raw_token)
        expires_at = verification_token_expiry()

        existing = await self.repo.get_by_user_id(session, current_user.id)

        if existing:
            # update existing record
            existing.token_hash = token_hash
            existing.expires_at = expires_at
            existing.used = False
        else:
            verification = EmailVerification(
                user_id=current_user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
            await self.repo.add(session, verification)

        await session.commit()
        return raw_token

    async def get_by_token(
        self,
        session: AsyncSession,
        raw_token: str,
    ) -> EmailVerification:
        token_hash = hash_verification_token(raw_token)

        verification = await self.repo.get_by_token_hash(session, token_hash)

        if (
            not verification
            or verification.used
            or verification.expires_at < datetime.now(UTC)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        return verification

    async def verify(
        self,
        session: AsyncSession,
        raw_token: str,
    ) -> Literal["verified", "already_verified"]:
        token_hash = hash_verification_token(raw_token)

        verification = await self.repo.get_by_token_hash_for_update(
            session,
            token_hash,
        )

        if not verification or verification.expires_at < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

        if verification.used:
            return "already_verified"

        verification.used = True
        verification.user.is_verified = True

        await session.commit()
        return "verified"

    async def cleanup(self, session: AsyncSession) -> int:
        deleted = await self.repo.delete_expired_or_used(session)
        await session.commit()
        return deleted


# Singleton
email_verification_service = EmailVerificationService()
