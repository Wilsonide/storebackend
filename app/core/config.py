from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    smtp_user: str
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    smtp_password: str
    domain: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    secret_key: str = "supersecretkeythatisatleast32chars!"
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_PUBLIC_KEY: str

    PAYSTACK_BASE_URL: str = "https://api.paystack.co"

    PAYSTACK_CALLBACK_URL: str

    PAYSTACK_CURRENCY: str = "NGN"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
