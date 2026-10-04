from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.users import User
from app.repositories.user_repository import (
    user_repository,
)
from app.schemas.user import UserCreate
from app.utils.helper import hash_password


class UserService:
    async def get_all_users(self, session):
        return await user_repository.get_all_users(session)

    async def get_user_by_id(
        self,
        session,
        user_id,
    ):
        return await user_repository.get_user_by_id(
            session,
            user_id,
        )

    async def get_user(
        self,
        session,
        user_email: str,
    ):
        return await user_repository.get_user_by_email(
            session,
            user_email,
        )

    async def get_user_by_refresh(
        self,
        session,
        token: str,
    ):
        return await user_repository.get_user_by_refresh_token(
            session,
            token,
        )

    async def create_user(
        self,
        session,
        *,
        data: UserCreate,
    ):
        email = data.email.lower()

        user = User(
            email=email,
            user_name=data.user_name,
            name=data.name,
            hashed_password=hash_password(data.password),
            is_verified=False,
        )

        try:
            return await user_repository.create_user(
                session,
                user,
            )

        except IntegrityError:
            await session.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            ) from None

    async def set_user_refresh_token(
        self,
        session,
        user: User,
        refresh_token_hash: str,
    ):
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.refresh_token_expire_days,
        )

        if user.refresh_token:
            user.refresh_token.token = refresh_token_hash
            user.refresh_token.expires_at = expires_at

        else:
            user.refresh_token = RefreshToken(
                token=refresh_token_hash,
                user_id=user.id,
                expires_at=expires_at,
            )

        return await user_repository.save(
            session,
            user,
        )

    async def update_user(
        self,
        session,
        *,
        user_email: str,
        update_data: dict,
    ):
        user = await user_repository.get_user_by_email(
            session,
            user_email,
        )

        if not user:
            return None

        return await user_repository.update_user(
            session,
            user,
            update_data,
        )

    async def delete_user(
        self,
        session,
        *,
        user_email: str,
    ):
        user = await user_repository.get_user_by_email(
            session,
            user_email,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        await user_repository.delete_user(
            session,
            user,
        )


user_service = UserService()
