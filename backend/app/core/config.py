"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "CrewAI Flow Manager"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://crewai:crewai@db:5432/crewai_flows"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://frontend:3000",
    ]
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "UTC"
    
    # CrewAI / LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")  # openai, ollama, custom
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
