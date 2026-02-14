"""
Application configuration
Load from environment variables
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # API Settings
    PROJECT_NAME: str = "Smart Finance API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS - Store as string internally
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # JWT
    JWT_SECRET: str = "53d08977-a2f4-44cd-a579-6094e6094b64"
    JWT_ALGORITHM: str = "HS256"
    
    # AI Models
    MODELS_PATH: str = "../models"
    EXPENSE_CLASSIFIER_PATH: str = "../models/expense_classifier.pkl"
    ANOMALY_DETECTOR_PATH: str = "../models/anomaly_detector.pkl"
    
    # Background Jobs
    ENABLE_BACKGROUND_JOBS: bool = False
    ROLLUP_SCHEDULE: str = "0 2 * * *"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
