from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.users import User
from app.utils.helper import JWTBearer

from .config import settings

oauth2_scheme = JWTBearer()


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    access_token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            access_token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as err:
        raise credentials_exception from err

    user = await session.get(User, UUID(user_id))
    if user.role == "system":
        raise HTTPException(
            status_code=403,
            detail="System users are not allowed to authenticate",
        )

    if user is None:
        raise credentials_exception
    return user


async def requires_verified_user(user: Annotated[User, Depends(get_current_user)]):
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        )
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]):
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
    return user


DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
VerifiedUser = Annotated[User, Depends(requires_verified_user)]
RequireAdmin = Annotated[User, Depends(require_admin)]
