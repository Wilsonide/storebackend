from math import ceil

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )


class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def calculate(
        cls,
        *,
        page: int,
        page_size: int,
        total: int,
    ):
        total_pages = ceil(total / page_size) if total else 0

        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )
