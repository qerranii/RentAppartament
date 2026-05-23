from typing import AsyncGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Column, DateTime, func
from app.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.SQLALCHEMY_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    connect_args={"server_settings": {"application_name": "apartment_rent"}}
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()


class BaseModel(Base):
    """
    Базовая модель для всех ORM моделей.
    
    Содержит общие поля: id, created_at, updated_at
    Все таблицы наследуют от этого класса.
    """
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """

    Yields:
        AsyncSession: Асинхронная сессия БД
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
