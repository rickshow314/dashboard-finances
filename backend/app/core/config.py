from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Configuración básica de la app
    APP_NAME: str
    DEBUG: bool
    ENVIRONMENT: str

    # API
    API_PREFIX: str
    BACKEND_CORS_ORIGINS: List[str]

    # Base de datos
    DATABASE_URL: str
    DATABASE_ECHO: bool = False  # Mostrar queries en desarrollo

    # Seguridad
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Configuración regional
    DEFAULT_CURRENCY: str
    DEFAULT_LANGUAGE: str

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
