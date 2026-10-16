from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.repositories.brand_repository import BrandRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    PaginatedProductResponse,
    ProductCreate,
    ProductQueryParams,
    ProductUpdate,
)


class ProductService:
    def __init__(
        self,
        repository: ProductRepository,
        category_repository: CategoryRepository,
        brand_repository: BrandRepository,
    ):
        self.repository = repository
        self.category_repository = category_repository
        self.brand_repository = brand_repository

    # ============================================================
    # IMAGE HELPERS
    # ============================================================

    @staticmethod
    def _attach_images(
        product: Product,
        images_data: list,
    ) -> None:
        """
        Replace a product's gallery and synchronize its legacy cover fields.

        If an image is marked is_cover=True, it becomes the cover.
        Otherwise, the first image becomes the cover.
        """
        product.images.clear()

        if not images_data:
            product.cover_image = None
            product.cover_public_id = None
            return

        selected_cover = next(
            (image for image in images_data if image.is_cover),
            images_data[0],
        )

        for index, image in enumerate(images_data):
            # The schema may default sort_order to 0. When multiple images
            # have that default, use their input order as a sensible fallback.
            sort_order = image.sort_order
            if sort_order is None or (sort_order == 0 and index > 0):
                sort_order = index

            product.images.append(
                ProductImage(
                    image_url=image.image_url,
                    public_id=image.public_id,
                    sort_order=sort_order,
                    is_cover=(image is selected_cover),
                )
            )

        product.cover_image = selected_cover.image_url
        product.cover_public_id = selected_cover.public_id

    # ============================================================
    # CREATE
    # ============================================================

    async def create(
        self,
        db: AsyncSession,
        data: ProductCreate,
    ) -> Product:
        # Validate category.
        category = await self.category_repository.get_by_id(
            db,
            data.category_id,
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

        # Validate brand.
        if data.brand_id is not None:
            brand = await self.brand_repository.get_by_id(
                db,
                data.brand_id,
            )

            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brand not found.",
                )

        # A product must have at least one variant.
        if not data.variants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A product must have at least one variant.",
            )

        # Only one variant can be the default.
        default_variants = [
            variant for variant in data.variants if variant.is_default
        ]

        if len(default_variants) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A product can have only one default variant.",
            )

        # Create product.
        product = Product(
            name=data.name.strip(),
            description=data.description.strip(),
            category_id=data.category_id,
            brand_id=data.brand_id,
            material=data.material.strip() if data.material else None,
            gender=data.gender.strip() if data.gender else None,
            warranty=data.warranty.strip() if data.warranty else None,
            cover_image=data.cover_image,
            cover_public_id=data.cover_public_id,
            is_available=data.is_available,
            is_featured=data.is_featured,
        )

        # Create product images.
        # If images are supplied, synchronize the legacy cover fields with
        # the selected gallery cover. If omitted/empty, preserve legacy
        # cover_image and cover_public_id supplied on the product.
        if data.images:
            self._attach_images(product, data.images)

        # Create variants.
        for variant_data in data.variants:
            variant = ProductVariant(
                price=variant_data.price,
                quantity=variant_data.quantity,
                color=(
                    variant_data.color.strip()
                    if variant_data.color
                    else None
                ),
                size=(
                    variant_data.size.strip()
                    if variant_data.size
                    else None
                ),
                is_default=variant_data.is_default,
                is_available=variant_data.is_available,
            )

            product.variants.append(variant)

        return await self.repository.create(db, product)

    # ============================================================
    # GET SINGLE PRODUCT
    # ============================================================

    async def get(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> Product:
        product = await self.repository.get_by_id(
            db,
            product_id,
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        return product

    # ============================================================
    # GET PAGINATED PRODUCTS
    # ============================================================

    async def get_paginated(
        self,
        db: AsyncSession,
        params: ProductQueryParams,
    ) -> PaginatedProductResponse:
        if (
            params.min_price is not None
            and params.max_price is not None
            and params.min_price > params.max_price
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_price cannot be greater than max_price.",
            )

        search = params.search.strip() if params.search else None

        products, total = await self.repository.get_paginated(
            db,
            page=params.page,
            page_size=params.page_size,
            search=search,
            category_id=params.category_id,
            brand_id=params.brand_id,
            featured=params.featured,
            available=params.available,
            min_price=params.min_price,
            max_price=params.max_price,
            sort=params.sort,
        )

        total_pages = (
            (total + params.page_size - 1) // params.page_size
            if total > 0
            else 0
        )

        return PaginatedProductResponse(
            items=products,
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1,
        )

    # ============================================================
    # GET ALL PRODUCTS
    # ============================================================

    async def get_all(
        self,
        db: AsyncSession,
        *,
        category_id: int | None = None,
        brand_id: int | None = None,
        featured: bool | None = None,
        available: bool | None = None,
    ) -> list[Product]:
        return await self.repository.get_all(
            db,
            category_id=category_id,
            brand_id=brand_id,
            featured=featured,
            available=available,
        )

    # ============================================================
    # SEARCH
    # ============================================================

    async def search(
        self,
        db: AsyncSession,
        search_term: str,
    ) -> list[Product]:
        search_term = search_term.strip()

        if not search_term:
            return []

        return await self.repository.search(
            db,
            search_term,
        )

    # ============================================================
    # UPDATE
    # ============================================================

    async def update(
        self,
        db: AsyncSession,
        product_id: int,
        data: ProductUpdate,
    ) -> Product:
        product = await self.get(db, product_id)

        # Capture image input before dumping fields. This preserves the
        # Pydantic image objects instead of converting them into dictionaries.
        images_were_supplied = "images" in data.model_fields_set
        images_data = data.images

        # Exclude images because the gallery is handled as a relationship,
        # not as a direct Product model column.
        values = data.model_dump(
            exclude_unset=True,
            exclude={"images"},
        )

        if not values and not images_were_supplied:
            return product

        # Validate category if changed.
        if "category_id" in values:
            category = await self.category_repository.get_by_id(
                db,
                values["category_id"],
            )

            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found.",
                )

        # Validate brand if changed.
        if "brand_id" in values and values["brand_id"] is not None:
            brand = await self.brand_repository.get_by_id(
                db,
                values["brand_id"],
            )

            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brand not found.",
                )

        # Normalize string fields.
        string_fields = (
            "name",
            "description",
            "material",
            "gender",
            "warranty",
        )

        for field in string_fields:
            if field in values and values[field] is not None:
                values[field] = values[field].strip()

        # Replace the gallery only when the client actually supplied images.
        # None means no gallery change; [] means remove all gallery images.
        if images_were_supplied and images_data is not None:
            self._attach_images(product, images_data)

            # Keep legacy cover fields synchronized with the gallery.
            # Remove any conflicting cover values from the normal update data.
            values.pop("cover_image", None)
            values.pop("cover_public_id", None)

            # These values are assigned directly to the product above, so the
            # repository doesn't need to set them again.
        elif images_were_supplied and images_data is None:
            # Explicit null is treated as no gallery change.
            pass

        # Apply normal product-field changes.
        return await self.repository.update(
            db,
            product,
            values,
        )

    # ============================================================
    # DELETE
    # ============================================================

    async def delete(
        self,
        db: AsyncSession,
        product_id: int,
    ) -> None:
        product = await self.get(db, product_id)

        await self.repository.delete(
            db,
            product,
        )