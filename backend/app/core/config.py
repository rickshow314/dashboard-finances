from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool
    ENVIRONMENT: str

    API_PREFIX: str
    BACKEND_CORS_ORIGINS: List[str]

    DATABASE_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DEFAULT_CURRENCY: str
    DEFAULT_LANGUAGE: str

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
