"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRequest(BaseModel):
    refresh_token: str


# Image Schemas
class ImageResponse(BaseModel):
    id: int
    prediction_id: int
    file_name: str
    file_size: int
    mime_type: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Prediction Schemas
class PredictionCreate(BaseModel):
    """Schema for creating a new prediction - only 10 fields required by model."""
    title: str = Field(..., min_length=1, max_length=255, description="Название/адрес объекта")
    region: str = Field(..., min_length=1, max_length=100, description="Регион")
    address: str = Field(..., min_length=1, max_length=255, description="Адрес")
    square: float = Field(..., gt=0, le=1000, description="Площадь в кв.м")
    floor: int = Field(..., ge=1, le=100, description="Текущий этаж")
    max_floor: int = Field(..., ge=1, le=100, description="Всего этажей в доме")
    metro: str = Field(..., min_length=1, max_length=100, description="Станция метро")
    rooms: int = Field(..., ge=1, le=10, description="Количество комнат")
    time: int = Field(..., ge=0, le=120, description="Время до метро в минутах")
    time_type: str = Field(default="walk", description="Тип пути: walk или transport")
    description: str = Field(default="", max_length=5000, description="Описание объекта")
    
    # Legacy fields (for compatibility with DB)
    city: Optional[str] = Field(None, max_length=100)
    street_type: Optional[str] = Field(None, max_length=50)
    district: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class PredictionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    district: Optional[str] = None


class PredictionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    region: str
    city: str
    metro: str
    street_type: str
    district: Optional[str]
    square: float
    rooms_clean: int
    floor: int
    max_floor: int
    time_to_metro: int
    latitude: Optional[float]
    longitude: Optional[float]
    predicted_price: float
    confidence_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class PredictionDetailResponse(PredictionResponse):
    pass


# Analytics Schemas
class PriceStatistics(BaseModel):
    min_price: float
    max_price: float
    avg_price: float
    median_price: float
    count: int


class DistrictStats(BaseModel):
    district: str
    avg_price: float
    count: int


class AnalyticsResponse(BaseModel):
    total_predictions: int
    price_stats: PriceStatistics
    by_district: List[DistrictStats]
