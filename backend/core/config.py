from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator


class Settings(BaseSettings):
    MONGO_URI: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400  # 24 hours in seconds
    HUGGINGFACE_API_KEY: str
    GEMINI_API_KEY: Optional[str] = None  # Optional for enhanced detection
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: Union[str, list] = "http://localhost:3000,http://localhost:5173"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Split comma-separated string into list
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

