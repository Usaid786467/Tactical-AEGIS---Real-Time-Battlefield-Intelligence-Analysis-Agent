"""
Configuration Management
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application Info
    APP_NAME: str = "Tactical AEGIS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./tactical_aegis.db"

    # Gemini AI
    GEMINI_API_KEY: str

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]

    # Map Services
    MAPBOX_ACCESS_TOKEN: str = ""
    OPENSTREETMAP_API_KEY: str = ""

    # Optional Services
    OPENWEATHER_API_KEY: str = ""
    SENTINEL_HUB_API_KEY: str = ""
    NASA_API_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    USE_REDIS: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: Path = Path("./uploads")

    # Analysis Settings
    THREAT_CONFIDENCE_THRESHOLD: float = 0.7
    MAX_CONCURRENT_ANALYSES: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            """Parse environment variables, especially lists"""
            if field_name == 'CORS_ORIGINS':
                return [origin.strip() for origin in raw_val.split(',')]
            return raw_val


# Create global settings instance
settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
