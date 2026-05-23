import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from pathlib import Path
from app.core.config import settings
from app.core.exceptions import InternalServerError
from app.utils.logger import logger


class ModelLoader:
    """Load and cache ML model dictionary."""
    
    _model_dict = None
    _model_path = None
    
    @classmethod
    def load_model(cls) -> Dict[str, Any]:
        """Load model from disk (singleton)."""
        if cls._model_dict is None:
            try:
                model_path = Path(settings.MODEL_PATH)
                if not model_path.exists():
                    raise FileNotFoundError(f"Model not found at {settings.MODEL_PATH}")

                import sys
                import builtins as _builtins
                added_alias = False
                try:
                    if '__builtin__' not in sys.modules:
                        sys.modules['__builtin__'] = _builtins
                        added_alias = True
                    try:
                        cls._model_dict = joblib.load(str(model_path))
                        cls._model_path = model_path
                    except Exception as e_joblib:
                        logger.warning(f"joblib.load failed ({e_joblib}), trying dill.load fallback")
                        try:
                            import dill
                            with open(str(model_path), 'rb') as fh:
                                cls._model_dict = dill.load(fh)
                                cls._model_path = model_path
                        except Exception as e_dill:
                            logger.error(f"dill.load also failed: {e_dill}")
                            raise
                finally:
                    if added_alias:
                        try:
                            del sys.modules['__builtin__']
                        except Exception:
                            pass
                

                if 'final_model' not in cls._model_dict:
                    raise ValueError("Model missing 'final_model' key")
                if 'selected_features' not in cls._model_dict and 'cb_features' in cls._model_dict:
                    cls._model_dict['selected_features'] = cls._model_dict.get('cb_features')
                if 'tfidf_vectorizer' not in cls._model_dict:
                    logger.warning("Model missing 'tfidf_vectorizer' - using dummy vectorizer that outputs zeros")
                    class DummyTfidf:
                        def transform(self, texts):
                            import numpy as _np
                            return _np.zeros((len(texts), 30))
                    cls._model_dict['tfidf_vectorizer'] = DummyTfidf()
                if 'target_encoder' not in cls._model_dict:
                    logger.warning("Model missing 'target_encoder' - using empty encoders")
                    cls._model_dict['target_encoder'] = {}
                if 'russian_stopwords' not in cls._model_dict:
                    logger.warning("Model missing 'russian_stopwords' - using empty set")
                    cls._model_dict['russian_stopwords'] = set()
                # Ensure selected_features exists
                if 'selected_features' not in cls._model_dict or not cls._model_dict['selected_features']:
                    logger.warning("Model missing 'selected_features' - attempting to infer from cb_features or tfidf size")
                    cls._model_dict['selected_features'] = cls._model_dict.get('selected_features', [])
                
                logger.info(f"Model loaded successfully. Features: {len(cls._model_dict['selected_features'])}")
                logger.info(f"Selected features sample: {cls._model_dict['selected_features'][:30]}")
                cat_info = cls._model_dict.get('cat_features') or cls._model_dict.get('categorical_features')
                logger.info(f"Model cat_features: {cat_info}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise InternalServerError(f"Failed to load model: {str(e)}")
        
        return cls._model_dict
    
    @classmethod
    def get_model(cls) -> Dict[str, Any]:
        return cls.load_model()


class FeaturePreprocessor:

    def __init__(self, model_dict: Dict[str, Any]):
        self.model_dict = model_dict
        self.selected_features = model_dict['selected_features']
        self.tfidf_vectorizer = model_dict['tfidf_vectorizer']
        self.target_encoder = model_dict['target_encoder']
        self.russian_stopwords = model_dict['russian_stopwords']
    
    def preprocess(
        self,
        square: float,
        floor: int,
        max_floor: int,
        rooms_clean: int,
        time_to_metro: int,
        region: str,
        city: str,
        metro: str,
        street_type: str,
        description: str = "",
        is_first_floor: bool = False,
        is_last_floor: bool = False,
        has_metro: bool = True,
        is_central: bool = False,
        has_furniture: bool = False,
        has_appliances: bool = False,
        has_tv: bool = False,
        has_wifi: bool = False,
        has_dishwasher: bool = False,
        has_washing_machine: bool = False,
        renovation_euro: bool = False,
        renovation_cosmetic: bool = False,
        renovation_new: bool = False,
        pets_allowed: bool = False,
        children_allowed: bool = False,
        has_parking: bool = False,
        has_balcony: bool = False,
        has_security: bool = False,
        is_new_building: bool = False,
        floor_category: str = "middle",
        building_height: str = "mid_rise",
        size_category: str = "medium",
        metro_accessibility: str = "medium",
        rooms_per_square: Optional[float] = None,
        **kwargs,
    ) -> np.ndarray:
        """

        Args:
            square: Apartment area in square meters
            floor: Current floor
            max_floor: Total floors in building
            rooms_clean: Number of rooms
            time_to_metro: Time to metro in minutes
            region: Region/Oblast name
            city: City name
            metro: Metro station name
            street_type: Street type (улица, переулок, etc.)
            description: Apartment description for TF-IDF
            Various boolean features for amenities
            
        Returns:
            np.ndarray: Array of shape (1, 76) with all preprocessed features
        """
        
        feature_dict = {}
        
        feature_dict['square'] = float(square)
        feature_dict['floor'] = int(floor)
        feature_dict['max_floor'] = int(max_floor)
        feature_dict['rooms_clean'] = int(rooms_clean)
        feature_dict['time_to_metro'] = int(time_to_metro)
        
        feature_dict['floor_ratio'] = float(floor) / max(int(max_floor), 1)
        if rooms_per_square is not None:
            try:
                feature_dict['rooms_per_square'] = float(rooms_per_square)
            except Exception:
                feature_dict['rooms_per_square'] = int(rooms_clean) / max(float(square), 1)
        else:
            feature_dict['rooms_per_square'] = int(rooms_clean) / max(float(square), 1)
        feature_dict['square_x_rooms'] = float(square) * int(rooms_clean)
        feature_dict['log_square'] = np.log1p(float(square))
        feature_dict['price_per_sqm_estimate'] = 0.0
        
        feature_dict['is_first_floor'] = int(is_first_floor)
        feature_dict['is_last_floor'] = int(is_last_floor)
        feature_dict['has_metro'] = int(has_metro)
        feature_dict['is_central'] = int(is_central)
        feature_dict['has_furniture'] = int(has_furniture)
        feature_dict['has_appliances'] = int(has_appliances)
        feature_dict['has_tv'] = int(has_tv)
        feature_dict['has_wifi'] = int(has_wifi)
        feature_dict['has_dishwasher'] = int(has_dishwasher)
        feature_dict['has_washing_machine'] = int(has_washing_machine)
        feature_dict['renovation_euro'] = int(renovation_euro)
        feature_dict['renovation_cosmetic'] = int(renovation_cosmetic)
        feature_dict['renovation_new'] = int(renovation_new)
        feature_dict['pets_allowed'] = int(pets_allowed)
        feature_dict['children_allowed'] = int(children_allowed)
        feature_dict['has_parking'] = int(has_parking)
        feature_dict['has_balcony'] = int(has_balcony)
        feature_dict['has_security'] = int(has_security)
        feature_dict['is_new_building'] = int(is_new_building)
        
        categorical_features = {
            'region': region,
            'city': city,
            'metro': metro,
            'street_type': street_type,
        }
        
        cat_encoded_dict = self._encode_categorical(categorical_features)
        feature_dict.update(cat_encoded_dict)
        
        floor_category_vals = self._one_hot_encode('floor_category', floor_category, ['low', 'middle', 'high'])
        feature_dict.update(floor_category_vals)
        
        building_height_vals = self._one_hot_encode('building_height', building_height, ['mid_rise', 'high_rise', 'skyscraper'])
        feature_dict.update(building_height_vals)
        
        size_category_vals = self._one_hot_encode('size_category', size_category, ['small', 'medium', 'large', 'huge'])
        feature_dict.update(size_category_vals)
        
        metro_accessibility_vals = self._one_hot_encode('metro_accessibility', metro_accessibility, ['close', 'medium', 'far'])
        feature_dict.update(metro_accessibility_vals)
        
        tfidf_features = self._process_description(description)
        feature_dict.update(tfidf_features)
        
        feature_array = np.array([
            feature_dict.get(feature_name, 0.0) 
            for feature_name in self.selected_features
        ], dtype=np.float32)
        
        return feature_array.reshape(1, -1)
    
    def _encode_categorical(self, categorical_dict: Dict[str, str]) -> Dict[str, float]:
        """Apply target encoding to categorical features."""
        result = {}
        for feature_name, value in categorical_dict.items():
            try:
                encoded_value = getattr(self.target_encoder, f'{feature_name}_encoder', {}).get(value, 0.0)
                result[feature_name] = float(encoded_value)
            except Exception as e:
                logger.warning(f"Failed to encode {feature_name}={value}: {e}")
                result[feature_name] = 0.0
        return result
    
    def _one_hot_encode(self, prefix: str, value: str, categories: List[str]) -> Dict[str, int]:
        result = {}
        for category in categories:
            key = f"{prefix}_{category}"
            result[key] = 1 if value == category else 0
        return result
    
    def _process_description(self, description: str) -> Dict[str, float]:
        """Process text description through TF-IDF vectorizer."""
        result = {}
        try:
            if not description or len(description.strip()) == 0:
                for i in range(30):
                    result[f'tfidf_{i}'] = 0.0
            else:
                words = description.lower().split()
                cleaned_words = [w for w in words if w not in self.russian_stopwords]
                cleaned_text = ' '.join(cleaned_words)
                
                tfidf_matrix = self.tfidf_vectorizer.transform([cleaned_text])
                tfidf_array = tfidf_matrix.toarray()[0]
                
                for i, value in enumerate(tfidf_array[:30]):
                    result[f'tfidf_{i}'] = float(value)
        except Exception as e:
            logger.warning(f"Failed to process description: {e}")
            for i in range(30):
                result[f'tfidf_{i}'] = 0.0
        
        return result


class ImageFeatureExtractor:
    """Extract features from images (placeholder)."""
    
    @staticmethod
    def extract_features(image_path: str) -> np.ndarray:
        """Extract features from image."""
        try:
            from PIL import Image
            
            img = Image.open(image_path)
            img = img.resize((224, 224))
            
            # Convert to numpy array
            img_array = np.array(img, dtype=np.float32) / 255.0
            
            # Simple features: mean color, brightness
            mean_color = np.mean(img_array, axis=(0, 1))
            brightness = np.mean(img_array)
            
            # Flatten
            features = np.concatenate([mean_color, [brightness]])
            
            return features
        except Exception as e:
            raise InternalServerError(f"Failed to extract image features: {str(e)}")
