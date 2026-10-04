from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BrandBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = None

    image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class BrandResponse(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
