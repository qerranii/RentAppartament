from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.exceptions import AuthenticationError, ConflictError
from app.models import User
from app.schemas import UserCreate


class AuthService:
    """

    Обрабатывает регистрацию, вход, валидацию токенов.
    Применяет бизнес-логику перед обращением к репозиторию.
    """
    
    def __init__(self, db: AsyncSession):
        """

        Args:
            db: Асинхронная сессия БД
        """
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, user_data: UserCreate) -> User:
        """

        Args:
            user_data: Данные для регистрации
        
        Returns:
            User: Созданный пользователь
        
        Raises:
            ConflictError: Email уже зарегистрирован
        """
        if await self.user_repo.email_exists(user_data.email):
            raise ConflictError(f"Email {user_data.email} уже зарегистрирован")
        
        hashed_password = hash_password(user_data.password)
        
        user = await self.user_repo.create({
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": user_data.full_name
        })
        
        return user
    
    async def authenticate(self, email: str, password: str) -> User:
        """

        Args:
            email: Email пользователя
            password: Пароль в открытом виде
        
        Returns:
            User: Пользователь если данные верны
        
        Raises:
            AuthenticationError: Неверный email/пароль или аккаунт неактивен
        """
        user = await self.user_repo.get_by_email(email)
        
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Неверный email или пароль")
        
        if not user.is_active:
            raise AuthenticationError("Аккаунт неактивен")
        
        return user
    
    async def get_user_by_token(self, token: str) -> User:
        """

        Args:
            token: JWT токен
        
        Returns:
            User: Пользователь если токен валиден
        
        Raises:
            AuthenticationError: Invalid token или пользователь не найден
        """
        user_id = verify_token(token)
        
        if not user_id:
            raise AuthenticationError("Неверный токен")
        
        user = await self.user_repo.get_by_id(int(user_id))
        
        if not user:
            raise AuthenticationError("Пользователь не найден")
        
        return user
    
    @staticmethod
    def create_tokens(user_id: int) -> dict:
        """

        Args:
            user_id: ID пользователя
        
        Returns:
            dict: {access_token, refresh_token, token_type}
        """
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
