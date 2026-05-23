"""Основное FastAPI приложение для платформы прогнозирования цен на аренду."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import AppException
from app.api.auth import router as auth_router
from app.api.predictions import router as predictions_router
from app.api.uploads import router as uploads_router
from app.utils.logger import logger
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    
    Выполняет инициализацию при запуске и очистку при завершении.
    """
    logger.info(f"Запуск {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Режим debug: {settings.DEBUG}")
    
    # Database initialization
    logger.info("Проверка и создание таблиц в БД (если необходимо)...")
    try:
        from app.models.database import engine, Base
        from app.models import User, Prediction, Image, PredictionLog

        async with engine.begin() as conn:
            logger.info(f"TABLES: {Base.metadata.tables.keys()}")
            await conn.run_sync(Base.metadata.create_all)
            # Ensure predictions table has new location columns; create_all does not ALTER existing tables.
            try:
                from sqlalchemy import text
                # Check and add columns if missing
                required_columns = {
                    'region': 'VARCHAR(100)',
                    'city': 'VARCHAR(100)',
                    'metro': 'VARCHAR(100)',
                    'street_type': 'VARCHAR(50)'
                }
                # Query existing columns
                res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'predictions'"))
                existing = {row[0] for row in res.fetchall()}
                for col, col_type in required_columns.items():
                    if col not in existing:
                        logger.info(f"Adding missing column '{col}' to predictions table")
                        await conn.execute(text(f"ALTER TABLE predictions ADD COLUMN {col} {col_type}"))
            except Exception as e:
                logger.error(f"Error ensuring prediction columns: {e}")
        await engine.dispose()
        logger.info("Таблицы БД созданы/проверены успешно")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")

    # ML Model loading
    logger.info("Инициализация ML модели...")
    try:
        from app.ml.model_loader import ModelLoader
        ModelLoader.load_model()
        logger.info("Модель загружена успешно")
    except Exception as e:
        logger.error(f"Ошибка при загрузке модели: {e}")
    
    yield
    logger.info("Завершение работы приложения")


app = FastAPI(
    title=settings.APP_NAME,
    description="Микросервисная платформа для прогнозирования цен на аренду квартир с ИИ",
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """Обработчик пользовательских исключений приложения."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get("/health")
async def health_check():
    """
    Проверка здоровья приложения.
    
    Используется docker-compose для health checks и load balancer.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION
    }


@app.get("/")
async def root():
    """
    Root endpoint - информация о приложении.
    """
    return {
        "message": f"Добро пожаловать в {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs"
    }


Instrumentator().instrument(app).expose(app, endpoint="/metrics")


app.include_router(auth_router)
app.include_router(predictions_router)
app.include_router(uploads_router)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
