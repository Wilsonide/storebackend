from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str | None = None
    name: str | None = None
    user_name: str | None = None


class ResetRequest(BaseModel):
    email: str


class ResetConfirmRequest(BaseModel):
    token: str
    new_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: str
    user_name: str | None = None
    name: str
    role: str
    is_verified: bool
    access_token: str | None = None  # <--- make optional

    model_config = ConfigDict(from_attributes=True)
