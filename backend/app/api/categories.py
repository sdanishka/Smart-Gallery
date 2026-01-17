"""
Smart Gallery Backend - Categories API Routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.core.database import get_db
from app.models.schemas import CategoryResponse, GalleryStats
from app.services.photo_service import photo_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all detected object categories with counts.
    
    Returns a list of all unique object types detected across all photos,
    along with the count of detections and photo IDs.
    """
    return await photo_service.get_categories(db)


@router.get("/stats", response_model=GalleryStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Get gallery statistics.
    
    Returns:
    - total_photos: Total number of photos
    - total_faces: Total faces detected
    - total_people: Number of unique people (clusters)
    - total_objects: Total object detections
    - categories: Object counts by category
    - storage_used: Total storage in bytes
    """
    return await photo_service.get_stats(db)
