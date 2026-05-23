"""Утилиты безопасности для JWT и обработки паролей."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Payload JWT токена."""
    sub: str
    exp: datetime
    token_type: str = "access"


def hash_password(password: str) -> str:
    """
    Args:
        password: Пароль в открытом виде
    
    Returns:
        str: Хеш пароля
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Сохраненный хеш пароля
    
    Returns:
        bool: True если пароли совпадают, иначе False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Args:
        subject: ID пользователя для токена
        expires_delta: Опциональное время жизни токена
    
    Returns:
        str: Закодированный JWT токен
    
    Example:
        token = create_access_token("123")
        # Используется: Authorization: Bearer <token>
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Args:
        subject: ID пользователя для токена
    
    Returns:
        str: Закодированный JWT refresh токен
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Args:
        token: JWT токен для проверки
    
    Returns:
        Optional[str]: ID пользователя если токен валиден, иначе None
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None
