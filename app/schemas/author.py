from pydantic import BaseModel


class AuthorCreate(BaseModel):
    name: str
    bio: str | None = None
    image_url: str | None = None


class AuthorUpdate(BaseModel):
    name: str | None = None

    bio: str | None = None

    image_url: str | None = None


class AuthorResponse(AuthorCreate):
    id: int

    class Config:
        from_attributes = True


class BookOut(BaseModel):
    id: int
    title: str
    cover_image: str | None = None

    class Config:
        from_attributes = True


class AuthorOut(BaseModel):
    id: int
    name: str
    bio: str | None = None
    image_url: str | None = None
    books: list[BookOut] = []

    class Config:
        from_attributes = True
