"""
Smart Gallery Backend - Search API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.core.database import get_db
from app.models.schemas import SearchResponse, SearchResult, PhotoResponse
from app.services.search_service import search_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/text", response_model=SearchResponse)
async def search_by_text(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search photos using natural language via CLIP.
    
    Examples:
    - "sunset on the beach"
    - "people playing soccer"
    - "red car on the street"
    - "family dinner"
    - "dog playing in park"
    
    The search uses CLIP embeddings to find semantically similar photos,
    not just keyword matching.
    """
    results = await search_service.search_by_text(db, q, limit)
    
    return SearchResponse(
        results=results,
        query=q,
        total=len(results),
    )


@router.post("/image", response_model=SearchResponse)
async def search_by_image(
    file: UploadFile = File(..., description="Reference image to search with"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search for visually similar photos using an uploaded image.
    
    Upload any image and find photos in your gallery that look similar.
    Uses CLIP embeddings to find semantically similar content.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images allowed.")
    
    content = await file.read()
    
    if len(content) > 10 * 1024 * 1024:  # 10MB limit for search
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB.")
    
    results = await search_service.search_by_image(db, content, limit)
    
    return SearchResponse(
        results=results,
        query=f"image:{file.filename}",
        total=len(results),
    )


@router.get("/face/{face_id}", response_model=SearchResponse)
async def search_by_face(
    face_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Find photos containing faces similar to the given face.
    
    Use this to find all photos of a specific person even if they
    haven't been clustered together yet.
    """
    results = await search_service.search_by_face(db, face_id, limit)
    
    return SearchResponse(
        results=results,
        query=f"face:{face_id}",
        total=len(results),
    )


@router.get("/person/{cluster_id}", response_model=List[PhotoResponse])
async def search_by_person(
    cluster_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all photos containing a specific person (cluster).
    
    This returns all photos where the person appears, based on
    face clustering.
    """
    photos = await search_service.search_by_person(db, cluster_id, limit)
    return [PhotoResponse(**p.to_dict()) for p in photos]


@router.get("/object/{class_name}", response_model=List[PhotoResponse])
async def search_by_object(
    class_name: str,
    min_confidence: float = Query(0.5, ge=0.0, le=1.0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all photos containing a specific object type.
    
    Object types are COCO classes detected by YOLO:
    - person, bicycle, car, motorcycle, airplane, bus, train, truck, boat
    - traffic light, fire hydrant, stop sign, parking meter, bench
    - bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
    - backpack, umbrella, handbag, tie, suitcase
    - frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove
    - skateboard, surfboard, tennis racket
    - bottle, wine glass, cup, fork, knife, spoon, bowl
    - banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake
    - chair, couch, potted plant, bed, dining table, toilet
    - tv, laptop, mouse, remote, keyboard, cell phone
    - microwave, oven, toaster, sink, refrigerator
    - book, clock, vase, scissors, teddy bear, hair drier, toothbrush
    """
    photos = await search_service.search_by_object(db, class_name, min_confidence, limit)
    return [PhotoResponse(**p.to_dict()) for p in photos]
