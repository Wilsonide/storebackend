from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.email_verification import EmailVerification


class EmailVerificationRepository:
    async def get_by_token_hash(
        self,
        session: AsyncSession,
        token_hash: str,
    ) -> EmailVerification | None:
        stmt = (
            select(EmailVerification)
            .where(EmailVerification.token_hash == token_hash)
            .options(selectinload(EmailVerification.user))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_token_hash_for_update(
        self,
        session: AsyncSession,
        token_hash: str,
    ) -> EmailVerification | None:
        stmt = (
            select(EmailVerification)
            .where(EmailVerification.token_hash == token_hash)
            .options(selectinload(EmailVerification.user))
            .with_for_update()
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id,
    ) -> EmailVerification | None:
        stmt = (
            select(EmailVerification)
            .where(EmailVerification.user_id == user_id)
            .options(selectinload(EmailVerification.user))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, session: AsyncSession, verification: EmailVerification) -> None:
        session.add(verification)

    async def delete_expired_or_used(self, session: AsyncSession) -> int:
        stmt = delete(EmailVerification).where(
            (EmailVerification.expires_at < datetime.now(UTC))
            | (EmailVerification.used.is_(True)),
        )
        result = await session.execute(stmt)
        return result.rowcount
