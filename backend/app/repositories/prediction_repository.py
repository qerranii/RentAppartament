"""Prediction repository."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Prediction
from app.repositories.base_repository import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    """Repository for Prediction model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Prediction)
    
    async def get_user_predictions(
        self, 
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Prediction]:
        """Get all predictions for a user."""
        result = await self.db.execute(
            select(Prediction)
            .where(Prediction.user_id == user_id)
            .order_by(Prediction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_prediction_count(self, user_id: int) -> int:
        """Get prediction count for user."""
        result = await self.db.execute(
            select(Prediction).where(Prediction.user_id == user_id)
        )
        return len(result.scalars().all())
    
    async def get_by_user_and_id(
        self, 
        user_id: int, 
        prediction_id: int
    ) -> Optional[Prediction]:
        """Get prediction by user and prediction ID."""
        result = await self.db.execute(
            select(Prediction).where(
                and_(
                    Prediction.user_id == user_id,
                    Prediction.id == prediction_id
                )
            )
        )
        return result.scalar_one_or_none()
