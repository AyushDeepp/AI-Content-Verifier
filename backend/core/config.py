from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGO_URI: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400  # 24 hours in seconds
    HUGGINGFACE_API_KEY: str
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

