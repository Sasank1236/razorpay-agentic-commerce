import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RazorBuy AI Agentic Commerce"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./razorbuy.db"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Razorpay Settings (Test Mode)
    RAZORPAY_KEY_ID: str = "rzp_test_dummy_key_id"
    RAZORPAY_KEY_SECRET: str = "dummy_secret_key"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
