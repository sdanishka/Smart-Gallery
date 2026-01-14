"""
Smart Gallery Backend - Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ Bounding Box ============

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


# ============ Detection Schemas ============

class DetectionBase(BaseModel):
    class_name: str
    confidence: float
    bbox: BoundingBox


class DetectionResponse(DetectionBase):
    id: str
    
    class Config:
        from_attributes = True


# ============ Face Schemas ============

class FaceBase(BaseModel):
    confidence: float
    bbox: BoundingBox
    age: Optional[int] = None
    gender: Optional[str] = None


class FaceResponse(FaceBase):
    id: str
    cluster_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============ Photo Schemas ============

class PhotoBase(BaseModel):
    original_filename: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None


class PhotoCreate(PhotoBase):
    pass


class PhotoResponse(PhotoBase):
    id: str
    filename: str
    upload_date: datetime
    taken_date: Optional[datetime] = None
    is_favorite: bool = False
    detections: List[DetectionResponse] = []
    faces: List[FaceResponse] = []
    has_clip_embedding: bool = False
    
    class Config:
        from_attributes = True


class PhotoUpdate(BaseModel):
    is_favorite: Optional[bool] = None


# ============ Cluster Schemas ============

class ClusterBase(BaseModel):
    name: Optional[str] = None


class ClusterResponse(ClusterBase):
    id: str
    face_count: int
    representative_photo_id: Optional[str] = None
    photo_ids: List[str] = []
    
    class Config:
        from_attributes = True


class ClusterUpdate(BaseModel):
    name: str


# ============ Category Schemas ============

class CategoryResponse(BaseModel):
    name: str
    count: int
    photo_ids: List[str]


# ============ Stats Schemas ============

class GalleryStats(BaseModel):
    total_photos: int
    total_faces: int
    total_people: int
    total_objects: int
    categories: Dict[str, int]
    storage_used: int


# ============ Search Schemas ============

class TextSearchRequest(BaseModel):
    query: str
    limit: int = Field(default=20, ge=1, le=100)


class ImageSearchRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)


class SearchResult(BaseModel):
    photo: PhotoResponse
    similarity: float
    match_type: str  # 'semantic', 'face', 'object'


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: Optional[str] = None
    total: int


# ============ Upload Response ============

class UploadResponse(BaseModel):
    success: bool
    photos: List[PhotoResponse]
    errors: List[Dict[str, Any]] = []
