import cloudinary.uploader


class UploadService:

    async def delete_image(
        self,
        public_id: str,
    ):

        cloudinary.uploader.destroy(
            public_id,
        )


upload_service = UploadService()