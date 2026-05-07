from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator, Field


class Settings(BaseSettings):
    MONGO_URI: str = Field(alias='MONGODB_URL')
    JWT_SECRET: str = Field(alias='JWT_SECRET_KEY')
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400  # 24 hours in seconds
    HUGGINGFACE_API_KEY: Optional[str] = None  # Optional, not used anymore
    GEMINI_API_KEY: Optional[str] = None  # Optional for enhanced detection
    GROQ_API_KEY: Optional[str] = None  # For fast text detection
    SIGHTENGINE_API_USER: Optional[str] = None
    SIGHTENGINE_API_SECRET: Optional[str] = None
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: Optional[str] = None
    R2_PUBLIC_URL: Optional[str] = None
    R2_REGION: str = "auto"
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
        populate_by_name = True  # Allow both field name and alias


settings = Settings()

