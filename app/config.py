"""
config.py - Centralized configuration using pydantic-settings
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/db_name"
    USE_LOCAL_DB: bool = False

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_postgres_prefix(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # Groq AI
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Email (Resend or Gmail SMTP)
    RESEND_API_KEY: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str = "R.S Education Solution"
    BASE_URL: str = "https://rseducationsolution.in"

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Scheduler (cron: Sunday 9 AM)
    SCHEDULER_DAY_OF_WEEK: str = "sun"
    SCHEDULER_HOUR: int = 9
    SCHEDULER_MINUTE: int = 0

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 10   # API rate limit
    EMAIL_BATCH_SIZE: int = 10        # Emails sent per batch
    EMAIL_BATCH_DELAY: float = 1.0    # Seconds between batches
    ADMIN_API_KEY: str = "dev-secret-key"  # Override in .env

    # Retry
    MAX_EMAIL_RETRIES: int = 3
    RETRY_DELAY: float = 2.0          # Seconds between retries

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Don't crash if .env has extra variables
    )


settings = Settings()
