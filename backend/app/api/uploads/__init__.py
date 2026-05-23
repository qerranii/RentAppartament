"""Upload API endpoints."""
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.services.image_service import ImageService
from app.schemas import ImageResponse
from app.core.exceptions import AppException
from app.core.config import settings
from app.utils.auth_decorator import get_current_user


router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/images/{prediction_id}", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    prediction_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload image for prediction."""
    try:
        image_service = ImageService(db)
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_name = f"{uuid.uuid4()}{file_ext}"
        
        upload_path = Path(settings.UPLOAD_DIR) / str(prediction_id)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        file_path = str(upload_path / unique_name)
        
        # Save file
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # Process image
        await image_service.process_image(file_path)
        
        # Store in database
        image = await image_service.upload_image(
            prediction_id=prediction_id,
            file_path=file_path,
            file_name=file.filename,
            file_size=len(contents)
        )
        
        return image
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete image."""
    try:
        image_service = ImageService(db)
        await image_service.delete_image(image_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
