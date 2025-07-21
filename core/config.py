# ecommerce_api/core/config.py

from pydantic import BaseSettings, Field, AnyHttpUrl
from typing import List, Optional


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = Field(..., description="MongoDB connection string")
    MONGODB_DB_NAME: str = Field(default="ecommerce", description="MongoDB database name")

    # API metadata
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    PROJECT_NAME: str = "E-Commerce API"
    PROJECT_VERSION: str = "1.0.0"

    # CORS setup
    CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000"], description="Frontend origins allowed for CORS"
    )

    # JWT auth (optional)
    SECRET_KEY: Optional[str] = "super-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize global settings
settings = Settings()
