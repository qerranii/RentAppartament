"""Конфигурация приложения из переменных окружения."""
from typing import Set, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Конфигурация приложения из переменных окружения.
    
    Использует Pydantic для валидации и .env файлов для значений.
    Все значения типобезопасны и имеют значения по умолчанию.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    # Приложение
    APP_NAME: str = "ApartmentForRent"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Сервер
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # База данных
    DATABASE_URL: str = "postgresql://apartment_user:password@postgres:5432/apartment_rent"
    SQLALCHEMY_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # Загрузка файлов
    UPLOAD_DIR: str = "/app/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    ALLOWED_EXTENSIONS: Set[str] = {"jpg", "jpeg", "png", "webp"}

    # ML модель
    MODEL_PATH: str = "/app/rental_price_model.pkl"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://localhost:80",
        "http://localhost",
        "http://frontend:3000",
        "http://backend:8000",
        "http://nginx",
    ]

    # Логирование
    LOG_LEVEL: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    """
    Получить кешированный экземпляр Settings.
    
    LRU cache предотвращает пересоздание объекта Settings при каждом обращении.
    
    Returns:
        Settings: Глобальный объект конфигурации
    """
    return Settings()


settings = get_settings()
