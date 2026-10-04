from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token


class TokenRepository:
    async def create_token(self, session: AsyncSession, data: Token):
        session.add(data)
        await session.commit()
        await session.refresh(data)
        return data

    async def get_valid_token(self, session: AsyncSession, token_hash: str):
        stmt = select(Token).where(
            and_(
                Token.token_hash == token_hash,
                Token.used == False,
                Token.expires_at > datetime.utcnow(),
            )
        )

        result = await session.execute(stmt)
        return result.scalars().first()

    async def mark_used(self, session: AsyncSession, token: Token):
        token.used = True
        await session.commit()
