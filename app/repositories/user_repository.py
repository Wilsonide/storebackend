from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from app.models.refresh_token import RefreshToken
from app.models.users import User


class UserRepository:
    async def get_all_users(self, session):
        stmt = (
            select(User)
            .options(
                selectinload(User.refresh_token),
            )
            .order_by(desc(User.created_at))
        )

        result = await session.execute(stmt)

        return result.scalars().all()

    async def get_user_by_id(
        self,
        session,
        user_id,
    ):
        stmt = (
            select(User)
            .options(
                selectinload(User.refresh_token),
                selectinload(User.email_verification),
            )
            .where(User.id == user_id)
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        session,
        email: str,
    ):
        stmt = (
            select(User)
            .options(
                selectinload(User.refresh_token),
                selectinload(User.email_verification),
            )
            .where(User.email == email)
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_by_refresh_token(
        self,
        session,
        token: str,
    ):
        stmt = (
            select(User)
            .join(User.refresh_token)
            .options(selectinload(User.refresh_token))
            .where(RefreshToken.token == token)
            .with_for_update()
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_user(
        self,
        session,
        user: User,
    ):
        session.add(user)

        await session.commit()

        await session.refresh(user)

        return user

    async def update_user(
        self,
        session,
        user: User,
        update_data: dict,
    ):
        for key, value in update_data.items():
            setattr(user, key, value)

        await session.commit()

        await session.refresh(user)

        return user

    async def delete_user(
        self,
        session,
        user: User,
    ):
        await session.delete(user)

        await session.commit()

    async def save(
        self,
        session,
        user: User,
    ):
        await session.commit()

        await session.refresh(user)

        return user


user_repository = UserRepository()
