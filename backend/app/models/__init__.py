from typing import Optional
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.database import BaseModel


class User(BaseModel):
    """
    Модель пользователя.

    """
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
    )


class Prediction(BaseModel):
    """
    Модель прогноза цены на аренду.

    """
    __tablename__ = "predictions"
    
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Location
    region: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    metro: Mapped[str] = mapped_column(String(100))
    street_type: Mapped[str] = mapped_column(String(50))
    
    # Legacy field
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Property dimensions
    square: Mapped[float] = mapped_column(Float)
    rooms_clean: Mapped[int] = mapped_column(Integer)
    floor: Mapped[int] = mapped_column(Integer)
    max_floor: Mapped[int] = mapped_column(Integer)
    
    # Transport
    time_to_metro: Mapped[int] = mapped_column(Integer, default=15)
    
    # Legacy fields
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Result
    predicted_price: Mapped[float] = mapped_column(Float)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    user: Mapped["User"] = relationship("User", back_populates="predictions")
    images: Mapped[list["Image"]] = relationship(
        "Image", 
        back_populates="prediction",
        cascade="all, delete-orphan"
    )
    logs: Mapped[list["PredictionLog"]] = relationship(
        "PredictionLog", 
        back_populates="prediction",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_prediction_user_id', 'user_id'),
        Index('idx_prediction_region', 'region'),
    )


class Image(BaseModel):
    """
    Модель изображения объекта.
    """
    __tablename__ = "images"
    
    prediction_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("predictions.id", ondelete="CASCADE"),
        index=True
    )
    file_path: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(50))
    
    prediction: Mapped["Prediction"] = relationship(
        "Prediction", 
        back_populates="images"
    )
    
    __table_args__ = (
        Index('idx_image_prediction_id', 'prediction_id'),
    )


class PredictionLog(BaseModel):
    """
    Модель логов ML вывода.

    """
    __tablename__ = "prediction_logs"
    
    prediction_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("predictions.id", ondelete="CASCADE"),
        index=True
    )
    request_json: Mapped[dict] = mapped_column(JSON)
    response_json: Mapped[dict] = mapped_column(JSON)
    inference_time_ms: Mapped[float] = mapped_column(Float)
    
    prediction: Mapped["Prediction"] = relationship(
        "Prediction", 
        back_populates="logs"
    )
    
    __table_args__ = (
        Index('idx_log_prediction_id', 'prediction_id'),
    )
