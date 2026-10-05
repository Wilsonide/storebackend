from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import delete

from app.core.config import settings
from app.core.deps import CurrentUser, DBSession
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    ResetConfirmRequest,
    ResetRequest,
    UserCreate,
    UserLogin,
    UserOut,
)
from app.services.token_service import token_service
from app.services.user_service import UserService
from app.services.verification_service import email_verification_service
from app.utils.helper import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.utils.mail import send_reset_email, send_verification_email

router = APIRouter(tags=["Authentication"], prefix="/auth")

user_service = UserService()


@router.post("/register", response_model=dict)
async def signup(
    payload: UserCreate,
    session: DBSession,
    background_tasks: BackgroundTasks,
):
    """Signup a new user."""
    # Check if user already exists
    existing_user = await user_service.get_user(session, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    # Otherwise, create a regular user
    new_user = await user_service.create_user(session, data=payload)
    # Generate a new verification token and send it via email.
    raw_token = await email_verification_service.create(
        session,
        current_user_id=new_user.id,
    )

    # Send email asynchronously
    verification_link = f"{settings.frontend_url}/auth/verify-email?token={raw_token}"

    background_tasks.add_task(
        send_verification_email,
        to_email=new_user.email,
        verification_link=verification_link,
    )

    return {
        "message": "Signup successful, check your email for verification.",
        "user_id": new_user.id,
    }


@router.post("/login", response_model=UserOut)
async def login(
    credentials: UserLogin,
    response: Response,
    session: DBSession,
):
    """
    Authenticate user and return access + refresh tokens.

    Sets HTTP-only refresh token cookie.
    Accepts optional invite_token from query to join a team automatically.
    """
    # Fetch user by email
    user = await user_service.get_user(session, credentials.email.lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )

    # Create access + refresh tokens
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=timedelta(minutes=7)
    )
    refresh_token = create_refresh_token()
    refresh_token_hash = hash_refresh_token(refresh_token)
    # Save hashed refresh token in DB
    await user_service.set_user_refresh_token(
        session=session,
        user=user,
        refresh_token_hash=refresh_token_hash,
    )

    # Set refresh token cookie (HTTP-only)
    refresh_token_expire_seconds = 7 * 24 * 60 * 60  # 7 days

    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=refresh_token_expire_seconds,
        expires=refresh_token_expire_seconds,
        path="/",
    )

    print(
        f"User {user.email} logged in successfully. Access token {access_token} issued."
    )

    # Return structured user + access token
    return UserOut(
        id=user.id,
        access_token=access_token,
        email=user.email,
        user_name=user.user_name,
        name=user.name,
        role=user.role,
        is_verified=user.is_verified,
    )


@router.post("/refresh")
async def refresh_token(
    response: Response,
    session: DBSession,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refreshToken")] = None,
):
    if not refresh_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Missing refresh token"
        )

    token_hash = hash_refresh_token(refresh_token_cookie)

    user = await user_service.get_user_by_refresh(session=session, token=token_hash)
    if not user or not user.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token"
        )

    if user.refresh_token.expires_at and user.refresh_token.expires_at < datetime.now(
        UTC
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Refresh token expired",
        )

    # Optionally extend expiry (sliding window)
    user.refresh_token.expires_at = datetime.now(UTC) + timedelta(days=7)
    await session.commit()

    # Issue new access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=7),
    )

    # Set same refresh token cookie

    response.set_cookie(
        key="refreshToken",
        value=refresh_token_cookie,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        expires=7 * 24 * 60 * 60,
        path="/",
    )

    return {"access_token": access_token}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    session: DBSession,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refreshToken")] = None,
):
    if refresh_token_cookie:
        # Delete refresh token from DB (hashed version)
        await session.execute(
            delete(RefreshToken).where(
                RefreshToken.token == hash_refresh_token(refresh_token_cookie)
            ),
        )
        await session.commit()

    # Delete cookie on client
    response.delete_cookie(key="refreshToken", samesite="none", secure=True, path="/")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
async def get_current_user(current_user: CurrentUser):
    """Get the currently authenticated user's details."""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        user_name=current_user.user_name,
        name=current_user.name,
        role=current_user.role,
        is_verified=current_user.is_verified,
    )


@router.post("/reset")
async def request_reset(
    payload: ResetRequest, session: DBSession, background_tasks: BackgroundTasks
):
    result = await token_service.request_reset(session, payload.email)

    if result is None:
        # To prevent email enumeration, return same response even if email doesn't exist
        return {"message": "email not found"}
    reset_link = f"{settings.frontend_url}/auth/new-password?token={result['token']}"

    background_tasks.add_task(
        send_reset_email,
        to_email=result["email"],
        reset_link=reset_link,
    )

    return {"message": "Password reset link sent, check your email."}


@router.post("/reset/confirm")
async def confirm_reset(payload: ResetConfirmRequest, session: DBSession):
    await token_service.confirm_reset(session, payload.token, payload.new_password)

    return {"message": "Password reset successful"}
