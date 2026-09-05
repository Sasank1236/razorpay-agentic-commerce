import os
import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RazorBuy AI Agentic Commerce"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./razorbuy.db"
    
    # Google Gemini Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Razorpay Settings (Test Mode)
    RAZORPAY_KEY_ID: str = "rzp_test_dummy_key_id"
    RAZORPAY_KEY_SECRET: str = "dummy_secret_key"
    
    # CORS — accepts a plain URL, comma-separated string, or JSON array string
    # e.g. on Render you can just type:  https://your-app.vercel.app
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://razorpay-agentic-commerce-beige.vercel.app",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        Accept any of these formats from environment variables:
          - JSON array:        ["https://a.vercel.app","http://localhost:3000"]
          - Comma-separated:   https://a.vercel.app,http://localhost:3000
          - Single URL:        https://a.vercel.app
          - Already a list:    (passed through as-is)
        """
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            # Try JSON array first
            if v.startswith("["):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return parsed
                except json.JSONDecodeError:
                    pass
            # Comma-separated or single value
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def database_url_normalized(self) -> str:
        """Render injects postgres:// URLs; SQLAlchemy 2.x requires postgresql+psycopg2://"""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and "+" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

settings = Settings()
