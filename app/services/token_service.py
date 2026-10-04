import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.utils.helper import hash_password, hash_token


class TokenService:
    def __init__(self):
        self.repo = TokenRepository()
        self.user_repo = UserRepository()

    async def request_reset(self, session: AsyncSession, email: str):
        user = await self.user_repo.get_user_by_email(session, email)

        if user:
            # 🔥 DELETE OLD TOKENS FIRST (IDEMPOTENT FIX)
            await session.execute(delete(Token).where(Token.user_id == user.id))

        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)

        reset_record = Token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            used=False,
        )

        await self.repo.create_token(session, reset_record)

        return {
            "email": user.email,
            "token": token,
        }

    async def confirm_reset(self, session: AsyncSession, token: str, new_password: str):
        token_hash = hash_token(token)

        record = await self.repo.get_valid_token(session, token_hash)

        if not record:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = await self.user_repo.get_user_by_id(session, record.user_id)

        # 🔥 IDENTITY SAFETY: allow repeated clicks safely
        if record.used:
            return True  # already used → treat as success

        user.hashed_password = hash_password(new_password)

        record.used = True  # mark first

        await session.commit()

        return True


token_service = TokenService()
