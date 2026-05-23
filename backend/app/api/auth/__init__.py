from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.auth_service import AuthService
from app.schemas import UserCreate, TokenResponse, UserResponse, TokenRequest
from app.core.exceptions import AppException


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """

    Args:
        user_data: Данные пользователя (email, password, full_name)
        db: Database session (внедряется автоматически)
    
    Returns:
        TokenResponse: access_token, refresh_token, token_type
    
    Raises:
        HTTPException 409: Email уже зарегистрирован
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.register(user_data)
        tokens = auth_service.create_tokens(user.id)
        return tokens
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=TokenResponse)
async def login(
    email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """

    Args:
        email: Email пользователя
        password: Пароль (проверяется с bcrypt хешем)
        db: Database session (внедряется автоматически)
    
    Returns:
        TokenResponse: access_token, refresh_token, token_type
    
    Raises:
        HTTPException 401: Invalid email or password
        HTTPException 403: User account is inactive
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.authenticate(email, password)
        tokens = auth_service.create_tokens(user.id)
        return tokens
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_request: TokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """

    Args:
        token_request: Объект с refresh_token
        db: Database session (внедряется автоматически)
    
    Returns:
        TokenResponse: Новые access_token и refresh_token
    
    Raises:
        HTTPException 401: Invalid или истекший refresh token
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_token(token_request.refresh_token)
        tokens = auth_service.create_tokens(user.id)
        return tokens
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/logout")
async def logout():
    """
    Returns:
        dict: Сообщение об успешном выходе
    """
    return {"message": "Успешный выход из системы"}
