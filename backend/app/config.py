"""
Configuration settings for the KuroAI backend.
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "KuroAI"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Frontend URL
    
    # Simulation Settings
    TICK_INTERVAL: float = 1.0  # seconds
    MAX_NPCS: int = 10
    MEMORY_RETENTION_DAYS: int = 30
    
    class Config:
        case_sensitive = True

settings = Settings()
