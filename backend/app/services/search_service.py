"""
Smart Gallery Backend - Search Service
Handles semantic search using CLIP and face search.
"""
import numpy as np
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging

from app.models.database import Photo, Face
from app.models.schemas import SearchResult, PhotoResponse
from app.services.ml_service import ml_service
from app.services.vector_service import vector_service
from app.utils.image import load_image

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching photos using various methods."""
    
    async def search_by_text(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Search photos using natural language query via CLIP.
        
        Args:
            db: Database session
            query: Natural language search query
            limit: Maximum number of results
            
        Returns:
            List of SearchResult with photo and similarity score
        """
        # Get text embedding from CLIP
        text_embedding = ml_service.get_clip_text_embedding(query)
        
        # Search in vector index
        similar = vector_service.search_by_clip(text_embedding, k=limit)
        
        results = []
        for photo_id, similarity in similar:
            # Get full photo data
            result = await db.execute(
                select(Photo)
                .options(selectinload(Photo.detections), selectinload(Photo.faces))
                .where(Photo.id == photo_id)
            )
            photo = result.scalar_one_or_none()
            
            if photo:
                results.append(SearchResult(
                    photo=PhotoResponse(**photo.to_dict()),
                    similarity=similarity,
                    match_type='semantic'
                ))
        
        return results
    
    async def search_by_image(
        self,
        db: AsyncSession,
        image_bytes: bytes,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Search for similar photos using an uploaded image.
        
        Args:
            db: Database session
            image_bytes: Image file bytes
            limit: Maximum number of results
            
        Returns:
            List of SearchResult with photo and similarity score
        """
        # Load and get embedding
        image = load_image(image_bytes)
        query_embedding = ml_service.get_clip_image_embedding(image)
        
        # Search in vector index
        similar = vector_service.search_by_clip(query_embedding, k=limit)
        
        results = []
        for photo_id, similarity in similar:
            result = await db.execute(
                select(Photo)
                .options(selectinload(Photo.detections), selectinload(Photo.faces))
                .where(Photo.id == photo_id)
            )
            photo = result.scalar_one_or_none()
            
            if photo:
                results.append(SearchResult(
                    photo=PhotoResponse(**photo.to_dict()),
                    similarity=similarity,
                    match_type='semantic'
                ))
        
        return results
    
    async def find_similar_photos(
        self,
        db: AsyncSession,
        photo_id: str,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Find photos similar to a given photo using CLIP embeddings.
        
        Args:
            db: Database session
            photo_id: ID of the reference photo
            limit: Maximum number of results
            
        Returns:
            List of similar photos
        """
        # Get the photo's embedding
        result = await db.execute(
            select(Photo).where(Photo.id == photo_id)
        )
        photo = result.scalar_one_or_none()
        
        if not photo or not photo.clip_embedding:
            return []
        
        query_embedding = np.frombuffer(photo.clip_embedding, dtype=np.float32)
        
        # Search (exclude self by getting limit+1 and filtering)
        similar = vector_service.search_by_clip(query_embedding, k=limit + 1)
        
        results = []
        for pid, similarity in similar:
            if pid == photo_id:  # Skip self
                continue
            
            result = await db.execute(
                select(Photo)
                .options(selectinload(Photo.detections), selectinload(Photo.faces))
                .where(Photo.id == pid)
            )
            p = result.scalar_one_or_none()
            
            if p:
                results.append(SearchResult(
                    photo=PhotoResponse(**p.to_dict()),
                    similarity=similarity,
                    match_type='semantic'
                ))
        
        return results[:limit]
    
    async def search_by_face(
        self,
        db: AsyncSession,
        face_id: str,
        limit: int = 20,
    ) -> List[SearchResult]:
        """
        Find photos containing similar faces.
        
        Args:
            db: Database session
            face_id: ID of the reference face
            limit: Maximum number of results
            
        Returns:
            List of photos containing similar faces
        """
        # Get face embedding
        result = await db.execute(
            select(Face).where(Face.id == face_id)
        )
        face = result.scalar_one_or_none()
        
        if not face or not face.embedding:
            return []
        
        query_embedding = np.frombuffer(face.embedding, dtype=np.float32)
        
        # Search for similar faces
        similar_faces = vector_service.search_by_face(query_embedding, k=limit * 2)
        
        # Get unique photos
        seen_photos = set()
        results = []
        
        for fid, similarity in similar_faces:
            if fid == face_id:
                continue
            
            # Get face's photo
            result = await db.execute(
                select(Face).where(Face.id == fid)
            )
            similar_face = result.scalar_one_or_none()
            
            if similar_face and similar_face.photo_id not in seen_photos:
                seen_photos.add(similar_face.photo_id)
                
                # Get full photo
                result = await db.execute(
                    select(Photo)
                    .options(selectinload(Photo.detections), selectinload(Photo.faces))
                    .where(Photo.id == similar_face.photo_id)
                )
                photo = result.scalar_one_or_none()
                
                if photo:
                    results.append(SearchResult(
                        photo=PhotoResponse(**photo.to_dict()),
                        similarity=similarity,
                        match_type='face'
                    ))
                
                if len(results) >= limit:
                    break
        
        return results
    
    async def search_by_person(
        self,
        db: AsyncSession,
        cluster_id: str,
        limit: int = 100,
    ) -> List[Photo]:
        """
        Get all photos containing a specific person (cluster).
        
        Args:
            db: Database session
            cluster_id: ID of the face cluster
            limit: Maximum number of results
            
        Returns:
            List of photos
        """
        result = await db.execute(
            select(Photo)
            .options(selectinload(Photo.detections), selectinload(Photo.faces))
            .join(Face)
            .where(Face.cluster_id == cluster_id)
            .distinct()
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_object(
        self,
        db: AsyncSession,
        class_name: str,
        min_confidence: float = 0.5,
        limit: int = 100,
    ) -> List[Photo]:
        """
        Get all photos containing a specific object type.
        
        Args:
            db: Database session
            class_name: Object class name (e.g., 'dog', 'car')
            min_confidence: Minimum detection confidence
            limit: Maximum number of results
            
        Returns:
            List of photos
        """
        from app.models.database import Detection
        
        result = await db.execute(
            select(Photo)
            .options(selectinload(Photo.detections), selectinload(Photo.faces))
            .join(Detection)
            .where(
                Detection.class_name == class_name,
                Detection.confidence >= min_confidence
            )
            .distinct()
            .order_by(Photo.upload_date.desc())
            .limit(limit)
        )
        return result.scalars().all()


# Global instance
search_service = SearchService()
