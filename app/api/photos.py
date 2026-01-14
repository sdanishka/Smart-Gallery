"""
Smart Gallery Backend - Photos API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import aiofiles
import logging

from app.core.database import get_db
from app.core.config import settings
from app.models.schemas import PhotoResponse, PhotoUpdate, UploadResponse
from app.services.photo_service import photo_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post("/upload", response_model=UploadResponse)
async def upload_photos(
    files: List[UploadFile] = File(..., description="Image files to upload"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload one or more photos for processing.
    
    Each photo will be processed through:
    - YOLO object detection
    - InsightFace face detection & recognition
    - CLIP embedding generation
    - Automatic face clustering
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    processed_photos = []
    errors = []
    
    for file in files:
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith("image/"):
                errors.append({
                    "filename": file.filename,
                    "error": "Invalid file type. Only images are allowed."
                })
                continue
            
            # Read file content
            content = await file.read()
            
            if len(content) > 50 * 1024 * 1024:  # 50MB limit
                errors.append({
                    "filename": file.filename,
                    "error": "File too large. Maximum size is 50MB."
                })
                continue
            
            # Process and save
            photo = await photo_service.process_and_save_photo(
                db=db,
                file_content=content,
                original_filename=file.filename or "unknown.jpg",
            )
            
            processed_photos.append(PhotoResponse(**photo.to_dict()))
            logger.info(f"Processed photo: {file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return UploadResponse(
        success=len(processed_photos) > 0,
        photos=processed_photos,
        errors=errors,
    )


@router.get("", response_model=List[PhotoResponse])
async def list_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get all photos with pagination."""
    photos = await photo_service.get_all_photos(db)
    return [PhotoResponse(**p.to_dict()) for p in photos[skip:skip + limit]]


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific photo by ID."""
    photo = await photo_service.get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return PhotoResponse(**photo.to_dict())


@router.delete("/{photo_id}")
async def delete_photo(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a photo and all associated data."""
    success = await photo_service.delete_photo(db, photo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Photo not found")
    return {"success": True, "message": "Photo deleted"}


@router.get("/{photo_id}/image")
async def get_photo_image(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the full-size photo image."""
    photo = await photo_service.get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    photo_path = settings.photos_dir / photo.filename
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")
    
    async with aiofiles.open(photo_path, 'rb') as f:
        content = await f.read()
    
    return Response(
        content=content,
        media_type=photo.mime_type,
        headers={
            "Cache-Control": "public, max-age=31536000",
            "Content-Disposition": f'inline; filename="{photo.original_filename}"',
        }
    )


@router.get("/{photo_id}/thumbnail")
async def get_photo_thumbnail(
    photo_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the photo thumbnail."""
    photo = await photo_service.get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    thumbnail_path = settings.thumbnails_dir / photo.filename
    if not thumbnail_path.exists():
        # Fall back to full image
        thumbnail_path = settings.photos_dir / photo.filename
    
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    async with aiofiles.open(thumbnail_path, 'rb') as f:
        content = await f.read()
    
    return Response(
        content=content,
        media_type=photo.mime_type,
        headers={
            "Cache-Control": "public, max-age=31536000",
        }
    )


@router.patch("/{photo_id}", response_model=PhotoResponse)
async def update_photo(
    photo_id: str,
    update: PhotoUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update photo properties (e.g., favorite status)."""
    photo = await photo_service.get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    if update.is_favorite is not None:
        photo = await photo_service.update_favorite(db, photo_id, update.is_favorite)
    
    return PhotoResponse(**photo.to_dict())


@router.get("/{photo_id}/similar", response_model=List[dict])
async def get_similar_photos(
    photo_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Find photos similar to the given photo using CLIP embeddings."""
    from app.services.search_service import search_service
    
    results = await search_service.find_similar_photos(db, photo_id, limit)
    return [
        {
            "photo": r.photo.model_dump(),
            "similarity": r.similarity,
            "match_type": r.match_type,
        }
        for r in results
    ]
