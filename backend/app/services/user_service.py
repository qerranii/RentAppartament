"""User service."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models import User
from app.core.exceptions import NotFoundError


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.user_repo.get_by_id(user_id)
        
        if not user:
            raise NotFoundError("User")
        
        return user
    
    async def update_user_profile(self, user_id: int, data: dict) -> User:
        """Update user profile."""
        user = await self.user_repo.update(user_id, data)
        
        if not user:
            raise NotFoundError("User")
        
        return user
    
    async def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            raise NotFoundError("User")
        
        return user
