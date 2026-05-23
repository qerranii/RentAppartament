"""Эндпоинты управления прогнозами."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.prediction_service import PredictionService
from app.services.auth_service import AuthService
from app.schemas import PredictionCreate, PredictionResponse, PredictionDetailResponse
from app.core.exceptions import AppException
from app.utils.auth_decorator import get_current_user


router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_data: PredictionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Создание нового прогноза.
    
    Выполняет ML вывод на основе параметров недвижимости и сохраняет результат.
    
    Args:
        prediction_data: Параметры объекта (комнаты, площадь, этаж и т.д.)
        db: Database session
        current_user: Текущий авторизованный пользователь
    
    Returns:
        PredictionResponse: Созданный прогноз с predicted_price
    
    Raises:
        HTTPException 422: Ошибка валидации данных
        HTTPException 500: Ошибка ML вывода
    """
    try:
        prediction_service = PredictionService(db)
        prediction = await prediction_service.create_prediction(
            current_user.id,
            prediction_data.model_dump()
        )
        return prediction
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("", response_model=List[PredictionResponse])
async def list_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получение списка прогнозов пользователя.
    
    Возвращает пагинированный список всех прогнозов текущего пользователя,
    отсортированные по дате создания (новые сверху).
    
    Args:
        skip: Количество записей для пропуска (по умолчанию 0)
        limit: Количество записей для возврата (по умолчанию 20, максимум 100)
        db: Database session
        current_user: Текущий авторизованный пользователь
    
    Returns:
        List[PredictionResponse]: Список прогнозов
    
    Example:
        GET /predictions?skip=0&limit=20
    """
    try:
        prediction_service = PredictionService(db)
        predictions = await prediction_service.get_user_predictions(
            current_user.id,
            skip=skip,
            limit=limit
        )
        return predictions
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{prediction_id}", response_model=PredictionDetailResponse)
async def get_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получение деталей конкретного прогноза.
    
    Возвращает полную информацию о прогнозе включая изображения и логи вывода.
    
    Args:
        prediction_id: ID прогноза
        db: Database session
        current_user: Текущий авторизованный пользователь
    
    Returns:
        PredictionDetailResponse: Полная информация о прогнозе
    
    Raises:
        HTTPException 404: Прогноз не найден или не принадлежит пользователю
    """
    try:
        prediction_service = PredictionService(db)
        prediction = await prediction_service.get_prediction(
            current_user.id,
            prediction_id
        )
        return prediction
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Удаление прогноза.
    
    Удаляет прогноз и все связанные изображения (cascade delete).
    
    Args:
        prediction_id: ID прогноза для удаления
        db: Database session
        current_user: Текущий авторизованный пользователь
    
    Returns:
        None (204 No Content)
    
    Raises:
        HTTPException 404: Прогноз не найден
    """
    try:
        prediction_service = PredictionService(db)
        await prediction_service.delete_prediction(
            current_user.id,
            prediction_id
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/stats/analytics")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Получение аналитики пользователя.
    
    Возвращает статистику всех прогнозов: средняя цена, медиана, 
    распределение по районам, количество и т.д.
    
    Args:
        db: Database session
        current_user: Текущий авторизованный пользователь
    
    Returns:
        dict: Аналитика {avg_price, median_price, min_price, max_price, 
              total_predictions, by_district {...}}
    """
    try:
        prediction_service = PredictionService(db)
        analytics = await prediction_service.get_analytics(current_user.id)
        return analytics
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
