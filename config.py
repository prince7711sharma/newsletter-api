"""
config.py - Centralized configuration using pydantic-settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "student_counselling"
    USERS_COLLECTION: str = "users"

    # Groq AI
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-8b-8192"

    # Email (Resend)
    RESEND_API_KEY: str
    EMAIL_FROM: str = "RS Education <newsletter@rseducation.com>"
    EMAIL_FROM_NAME: str = "R.S Education"

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"

    # Scheduler (cron: Sunday 9 AM)
    SCHEDULER_DAY_OF_WEEK: str = "sun"
    SCHEDULER_HOUR: int = 9
    SCHEDULER_MINUTE: int = 0

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 10   # API rate limit
    EMAIL_BATCH_SIZE: int = 10        # Emails sent per batch
    EMAIL_BATCH_DELAY: float = 1.0    # Seconds between batches

    # Retry
    MAX_EMAIL_RETRIES: int = 3
    RETRY_DELAY: float = 2.0          # Seconds between retries

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
