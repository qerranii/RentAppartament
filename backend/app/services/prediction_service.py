import time
import numpy as np
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.prediction_repository import PredictionRepository
from app.models import Prediction, Image
from app.ml.model_loader import ModelLoader, FeaturePreprocessor
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.logger import logger


class PredictionService:
    """Service for prediction operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.prediction_repo = PredictionRepository(db)
        self.model_dict = ModelLoader.get_model()
        self.preprocessor = FeaturePreprocessor(self.model_dict)
        self.model = self.model_dict['final_model']
    
    async def create_prediction(self, user_id: int, data: dict) -> Prediction:
        """Create new prediction with ML inference using 10 input fields."""
        try:
            from app.ml.simple_preprocessor import preprocess_input
            
            # Prepare input data with only 10 required fields
            input_data = {
                'region': data.get('region'),
                'address': data.get('address'),
                'square': data.get('square'),
                'floor': data.get('floor'),
                'max_floor': data.get('max_floor'),
                'metro': data.get('metro'),
                'rooms': data.get('rooms'),
                'time': data.get('time'),
                'time_type': data.get('time_type', 'walk'),
                'description': data.get('description', ''),
            }
            
            # Preprocess to 76 features
            features = preprocess_input(input_data, self.model_dict)
            
            # Run inference
            start_time = time.time()
            log_prediction = float(self.model.predict(features)[0])
            # Model predicts log(price), so we need to apply exp()
            prediction = np.exp(log_prediction)
            inference_time = (time.time() - start_time) * 1000
            
            logger.info(f"Input: {input_data}, Log pred: {log_prediction:.4f}, Price: {prediction:.2f} ₽, Time: {inference_time:.2f}ms")
            
            # Extract city from region or use region as city
            region = data.get('region', 'Unknown')
            city = data.get('city')
            if not city:
                # Extract city from region (e.g., "Москва и МО" -> "Москва")
                city = region.split(' и ')[0] if ' и ' in region else region
            
            # Extract street_type from address if possible
            address = data.get('address', '')
            street_type = data.get('street_type')
            if not street_type:
                # Try to extract street type from address (e.g., "ул.", "пр.", "пл.", "переулок")
                common_types = ['ул.', 'пр.', 'пл.', 'переулок', 'бульвар', 'кв-л', 'тупик']
                for st in common_types:
                    if st in address:
                        street_type = st
                        break
                if not street_type:
                    street_type = 'улица'
            
            # Prepare data for storage in DB
            pred_data = {
                'user_id': user_id,
                'title': data.get('title', address or 'Квартира'),
                'description': data.get('description'),
                'region': region,
                'city': city,
                'metro': data.get('metro'),
                'street_type': street_type,
                'district': data.get('district'),
                'square': data.get('square'),
                'rooms_clean': data.get('rooms', 1),
                'floor': data.get('floor'),
                'max_floor': data.get('max_floor'),
                'time_to_metro': data.get('time', 15),
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'predicted_price': prediction,
                'confidence_score': None
            }
            
            pred_obj = await self.prediction_repo.create(pred_data)
            
            return pred_obj
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise ValidationError(f"Prediction failed: {str(e)}")
    
    async def get_prediction(self, user_id: int, prediction_id: int) -> Prediction:
        """Get prediction by ID."""
        prediction = await self.prediction_repo.get_by_user_and_id(user_id, prediction_id)
        
        if not prediction:
            raise NotFoundError("Prediction")
        
        return prediction
    
    async def get_user_predictions(
        self, 
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Prediction]:
        """Get all user predictions."""
        return await self.prediction_repo.get_user_predictions(user_id, skip, limit)
    
    async def get_user_predictions_count(self, user_id: int) -> int:
        """Get user predictions count."""
        return await self.prediction_repo.get_user_prediction_count(user_id)
    
    async def delete_prediction(self, user_id: int, prediction_id: int) -> bool:
        """Delete prediction."""
        prediction = await self.prediction_repo.get_by_user_and_id(user_id, prediction_id)
        
        if not prediction:
            raise NotFoundError("Prediction")
        
        await self.db.delete(prediction)
        await self.db.commit()
        return True
    
    async def get_analytics(self, user_id: int) -> dict:
        """Get analytics for user predictions."""
        predictions = await self.prediction_repo.get_user_predictions(
            user_id, skip=0, limit=1000
        )
        
        if not predictions:
            return {
                'total': 0,
                'avg_price': 0,
                'min_price': 0,
                'max_price': 0,
                'median_price': 0
            }
        
        prices = [p.predicted_price for p in predictions]
        
        return {
            'total': len(predictions),
            'avg_price': float(np.mean(prices)),
            'min_price': float(np.min(prices)),
            'max_price': float(np.max(prices)),
            'median_price': float(np.median(prices))
        }
