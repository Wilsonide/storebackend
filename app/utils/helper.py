import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from app.core.config import settings


# Hash a password using bcrypt
def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)

    # convert bytes -> string
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode("utf-8")[:72]

    return bcrypt.checkpw(
        password=password_byte_enc, hashed_password=hashed_password.encode("utf-8")
    )


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):  # noqa: FBT001, FBT002
        """
        Initializes a JWTBearer instance.

        Args:
            auto_error (bool, optional): Determines whether an error should be
                automatically raised if the authentication fails.
                Defaults to True.
        """
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Handles the authentication logic for JWT-based authentication.

        Args:
            request (Request): The incoming request object.

        Raises:
            HTTPException: If the authentication token is invalid or missing.

        Returns:
            str: The JWT token extracted from the request.

        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid authorization token")
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication token")
        return credentials.credentials


""" def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password) """


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def hash_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verification_token_expiry() -> datetime:
    return datetime.now(UTC) + timedelta(hours=24)


def generate_invite_token() -> str:
    return secrets.token_urlsafe(32)


def hash_invite_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def invite_token_expiry() -> datetime:
    return datetime.now(UTC) + timedelta(hours=24)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
