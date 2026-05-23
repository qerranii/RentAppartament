"""Image service."""
import os
import shutil
from pathlib import Path
from typing import List
from PIL import Image as PILImage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Image, Prediction
from app.core.config import settings
from app.core.exceptions import ValidationError, NotFoundError


class ImageService:
    """Service for image operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_image(
        self,
        prediction_id: int,
        file_path: str,
        file_name: str,
        file_size: int
    ) -> Image:
        """Store image record in database."""
        # Get MIME type
        mime_type = self._get_mime_type(file_name)
        
        # Validate
        if not self._is_allowed_file(file_name):
            raise ValidationError(f"File type not allowed: {file_name}")
        
        if file_size > settings.MAX_FILE_SIZE:
            raise ValidationError(f"File size exceeds maximum: {file_size}")
        
        # Verify prediction exists
        result = await self.db.execute(
            select(Prediction).where(Prediction.id == prediction_id)
        )
        if not result.scalar_one_or_none():
            raise NotFoundError("Prediction")
        
        # Create image record
        image = Image(
            prediction_id=prediction_id,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type
        )
        
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        
        return image
    
    async def get_prediction_images(self, prediction_id: int) -> List[Image]:
        """Get all images for prediction."""
        result = await self.db.execute(
            select(Image).where(Image.prediction_id == prediction_id)
        )
        return result.scalars().all()
    
    async def delete_image(self, image_id: int) -> bool:
        """Delete image."""
        result = await self.db.execute(
            select(Image).where(Image.id == image_id)
        )
        image = result.scalar_one_or_none()
        
        if not image:
            raise NotFoundError("Image")
        
        # Delete file if exists
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        
        await self.db.delete(image)
        await self.db.commit()
        
        return True
    
    async def process_image(self, file_path: str) -> str:
        """Process and optimize image."""
        try:
            img = PILImage.open(file_path)
            
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = PILImage.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Resize if too large
            max_width, max_height = 1920, 1440
            img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
            
            # Save optimized
            img.save(file_path, quality=85, optimize=True)
            
            return file_path
        except Exception as e:
            raise ValidationError(f"Image processing failed: {str(e)}")
    
    @staticmethod
    def _is_allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in settings.ALLOWED_EXTENSIONS
    
    @staticmethod
    def _get_mime_type(filename: str) -> str:
        """Get MIME type from filename."""
        ext = filename.rsplit('.', 1)[1].lower()
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/jpeg')
