"""Simple preprocessing to convert 10 input fields to 39 model features."""
import numpy as np
import pandas as pd
from typing import Dict, Any


def preprocess_input(data: Dict[str, Any], model_dict: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert 10 input fields to 39 model features using model's helper functions.
    
    Input fields:
    - region: str
    - address: str  
    - square: float
    - floor: int
    - max_floor: int
    - metro: str
    - rooms: int/str
    - time: int
    - time_type: str
    - description: str
    
    Returns:
    - pandas.DataFrame with 39 columns matching model's cb_features
    """
    
    # Extract model components
    cb_features = model_dict.get('cb_features') or model_dict.get('selected_features') or []
    helpers = {
        'extract_city': model_dict.get('extract_city'),
        'extract_street_type': model_dict.get('extract_street_type'),
        'clean_text': model_dict.get('clean_text'),
        'extract_keywords': model_dict.get('extract_keywords'),
        'is_central_metro': model_dict.get('is_central_metro'),
        'lemmatize': model_dict.get('lemmatize'),
        'central_stations': model_dict.get('central_stations'),
    }
    russian_stopwords = model_dict.get('russian_stopwords', set())
    
    # Parse raw 10-field inputs
    region = str(data.get('region', '') or '')
    address = str(data.get('address', '') or '')
    square = float(data.get('square', 0.0))
    floor = int(data.get('floor', 0))
    max_floor = int(data.get('max_floor', 0))
    metro = str(data.get('metro', '') or '')
    rooms = data.get('rooms', 0)
    if isinstance(rooms, str):
        try:
            rooms = int(rooms)
        except:
            rooms = 0
    else:
        rooms = int(rooms)
    time_to_metro = int(data.get('time', 0))
    time_type = str(data.get('time_type', 'walk') or 'walk')
    description = str(data.get('description', '') or '')
    
    # Build feature dict for all 39 features
    features = {}
    
    for fname in cb_features:
        if fname == 'square':
            features['square'] = square
        elif fname == 'floor':
            features['floor'] = floor
        elif fname == 'max_floor':
            features['max_floor'] = max_floor
        elif fname in ('rooms', 'rooms_clean'):
            features[fname] = rooms
        elif fname in ('time', 'time_to_metro'):
            features[fname] = time_to_metro
        elif fname == 'is_first_floor':
            features['is_first_floor'] = 1 if floor == 1 else 0
        elif fname == 'is_last_floor':
            features['is_last_floor'] = 1 if floor == max_floor else 0
        elif fname == 'floor_ratio':
            features['floor_ratio'] = floor / max(max_floor, 1)
        elif fname == 'has_metro':
            features['has_metro'] = 1 if metro and len(metro) > 0 else 0
        elif fname == 'is_central':
            # Use helper if available
            if helpers['is_central_metro']:
                try:
                    features['is_central'] = 1 if helpers['is_central_metro'](metro) else 0
                except:
                    features['is_central'] = 0
            else:
                features['is_central'] = 0
        elif fname == 'rooms_per_square':
            features['rooms_per_square'] = rooms / max(square, 1)
        elif fname == 'square_x_rooms':
            features['square_x_rooms'] = square * rooms
        elif fname == 'log_square':
            features['log_square'] = np.log1p(square)
        elif fname == 'price_per_sqm_estimate':
            features['price_per_sqm_estimate'] = 0.0
        elif fname == 'metro_very_far':
            features['metro_very_far'] = 1 if time_to_metro > 30 else 0
        elif fname == 'region':
            features['region'] = region
        elif fname == 'city':
            # Use helper to extract city from address
            if helpers['extract_city']:
                try:
                    features['city'] = helpers['extract_city'](address)
                except:
                    # fallback: use region
                    features['city'] = region.split(' и ')[0] if ' и ' in region else region
            else:
                features['city'] = region.split(' и ')[0] if ' и ' in region else region
        elif fname == 'metro':
            features['metro'] = metro
        elif fname == 'street_type':
            # Use helper to extract street type from address
            if helpers['extract_street_type']:
                try:
                    features['street_type'] = helpers['extract_street_type'](address)
                except:
                    features['street_type'] = ''
            else:
                features['street_type'] = ''
        elif fname == 'description_clean':
            # Use helper to clean text
            if helpers['clean_text']:
                try:
                    features['description_clean'] = helpers['clean_text'](description)
                except:
                    features['description_clean'] = description
            else:
                features['description_clean'] = description
        elif fname == 'floor_category':
            # Categorize floor based on max_floor
            if floor <= 3:
                features['floor_category'] = 'low'
            elif floor <= 7:
                features['floor_category'] = 'middle'
            else:
                features['floor_category'] = 'high'
        elif fname == 'building_height':
            # Categorize building height based on max_floor
            if max_floor <= 5:
                features['building_height'] = 'low_rise'
            elif max_floor <= 12:
                features['building_height'] = 'mid_rise'
            elif max_floor <= 20:
                features['building_height'] = 'high_rise'
            else:
                features['building_height'] = 'skyscraper'
        elif fname == 'size_category':
            # Categorize apartment size
            if square <= 30:
                features['size_category'] = 'small'
            elif square <= 60:
                features['size_category'] = 'medium'
            elif square <= 100:
                features['size_category'] = 'large'
            else:
                features['size_category'] = 'huge'
        elif fname == 'metro_accessibility':
            # Categorize metro accessibility based on time
            if time_to_metro <= 10:
                features['metro_accessibility'] = 'close'
            elif time_to_metro <= 30:
                features['metro_accessibility'] = 'medium'
            else:
                features['metro_accessibility'] = 'far'
        else:
            # All remaining boolean features default to 0
            features[fname] = 0
    
    # Create DataFrame with all features in correct order
    df = pd.DataFrame([{k: features.get(k, 0) for k in cb_features}])
    
    # Ensure correct dtypes for categorical columns
    cat_cols = ['region', 'city', 'metro', 'street_type', 'description_clean', 
                'floor_category', 'building_height', 'size_category', 'metro_accessibility']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
    
    return df  # DataFrame with 39 columns in correct order
