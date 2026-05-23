from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.auth_service import AuthService
from app.core.exceptions import AuthenticationError


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """

    Args:
        credentials: HTTP credentials из Authorization header
        db: Database session
    
    Returns:
        User: Объект пользователя если токен валиден
    
    Raises:
        HTTPException 401: Invalid or expired token
    
    Example:
        @router.get("/protected")
        async def protected_endpoint(current_user = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_token(credentials.credentials)
        return user

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
