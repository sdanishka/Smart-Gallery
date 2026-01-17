"""
Smart Gallery Backend - Photo Service
Handles photo CRUD operations and processing pipeline.
"""
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
import logging
import aiofiles
import os

from app.models.database import Photo, Detection, Face, Cluster
from app.models.schemas import PhotoResponse, GalleryStats, CategoryResponse
from app.core.config import settings
from app.services.ml_service import ml_service
from app.services.vector_service import vector_service
from app.services.clustering_service import clustering_service
from app.utils.image import (
    load_image, resize_image, create_thumbnail, save_image,
    generate_filename, extract_exif, get_taken_date,
    get_image_dimensions, get_mime_type
)

logger = logging.getLogger(__name__)


class PhotoService:
    """Service for photo operations."""
    
    async def process_and_save_photo(
        self,
        db: AsyncSession,
        file_content: bytes,
        original_filename: str,
    ) -> Photo:
        """
        Process an uploaded photo through the ML pipeline and save it.
        
        Args:
            db: Database session
            file_content: Raw image bytes
            original_filename: Original filename from upload
            
        Returns:
            Created Photo object
        """
        # Generate unique filename
        filename = generate_filename(original_filename, file_content)
        
        # Load and prepare image
        image = load_image(file_content)
        image = resize_image(image)  # Resize if too large
        
        # Get dimensions
        width, height = get_image_dimensions(image)
        
        # Extract EXIF data
        exif_data = extract_exif(file_content)
        taken_date = get_taken_date(exif_data)
        
        # Create photo record
        photo = Photo(
            filename=filename,
            original_filename=original_filename,
            file_size=len(file_content),
            mime_type=get_mime_type(original_filename),
            width=width,
            height=height,
            exif_data=exif_data if exif_data else None,
            taken_date=taken_date,
        )
        db.add(photo)
        await db.flush()  # Get the ID
        
        try:
            # Save full image
            photo_path = settings.photos_dir / filename
            save_image(image, photo_path)
            
            # Create and save thumbnail
            thumbnail = create_thumbnail(image)
            thumbnail_path = settings.thumbnails_dir / filename
            save_image(thumbnail, thumbnail_path)
            
            # Run ML processing
            await self._process_photo_ml(db, photo, image)
            
            photo.processed = True
            
        except Exception as e:
            logger.error(f"Error processing photo {filename}: {e}")
            photo.processing_error = str(e)
        
        await db.commit()
        
        # Save vector indices
        vector_service.save_all()
        
        return photo
    
    async def _process_photo_ml(
        self,
        db: AsyncSession,
        photo: Photo,
        image: np.ndarray
    ):
        """Run ML models on the photo."""
        
        # 1. YOLO Object Detection
        try:
            detections = ml_service.detect_objects(image)
            for det in detections:
                detection = Detection(
                    photo_id=photo.id,
                    class_name=det["class_name"],
                    confidence=det["confidence"],
                    bbox_x1=det["bbox"]["x1"],
                    bbox_y1=det["bbox"]["y1"],
                    bbox_x2=det["bbox"]["x2"],
                    bbox_y2=det["bbox"]["y2"],
                )
                db.add(detection)
            logger.debug(f"Detected {len(detections)} objects in {photo.filename}")
        except Exception as e:
            logger.error(f"YOLO detection failed for {photo.filename}: {e}")
        
        # 2. Face Detection & Recognition
        try:
            faces = ml_service.detect_faces(image)
            for face_data in faces:
                face = Face(
                    photo_id=photo.id,
                    confidence=face_data["confidence"],
                    bbox_x1=face_data["bbox"]["x1"],
                    bbox_y1=face_data["bbox"]["y1"],
                    bbox_x2=face_data["bbox"]["x2"],
                    bbox_y2=face_data["bbox"]["y2"],
                    age=face_data.get("age"),
                    gender=face_data.get("gender"),
                )
                
                # Store embedding
                if face_data.get("embedding") is not None:
                    embedding = face_data["embedding"]
                    face.embedding = embedding.tobytes()
                    
                    db.add(face)
                    await db.flush()  # Get face ID
                    
                    # Add to vector index
                    vector_service.add_face_embedding(face.id, embedding)
                    
                    # Assign to cluster
                    await clustering_service.assign_face_to_cluster(db, face, embedding)
                else:
                    db.add(face)
            
            logger.debug(f"Detected {len(faces)} faces in {photo.filename}")
        except Exception as e:
            logger.error(f"Face detection failed for {photo.filename}: {e}")
        
        # 3. CLIP Embedding
        try:
            clip_embedding = ml_service.get_clip_image_embedding(image)
            photo.clip_embedding = clip_embedding.tobytes()
            
            # Add to vector index
            vector_service.add_clip_embedding(photo.id, clip_embedding)
            
            logger.debug(f"Generated CLIP embedding for {photo.filename}")
        except Exception as e:
            logger.error(f"CLIP embedding failed for {photo.filename}: {e}")
    
    async def get_photo(self, db: AsyncSession, photo_id: str) -> Optional[Photo]:
        """Get a photo by ID with all relationships loaded."""
        result = await db.execute(
            select(Photo)
            .options(selectinload(Photo.detections), selectinload(Photo.faces))
            .where(Photo.id == photo_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_photos(self, db: AsyncSession) -> List[Photo]:
        """Get all photos with relationships."""
        result = await db.execute(
            select(Photo)
            .options(selectinload(Photo.detections), selectinload(Photo.faces))
            .order_by(Photo.upload_date.desc())
        )
        return result.scalars().all()
    
    async def delete_photo(self, db: AsyncSession, photo_id: str) -> bool:
        """Delete a photo and all associated data."""
        photo = await self.get_photo(db, photo_id)
        if not photo:
            return False
        
        # Remove from vector indices
        vector_service.remove_photo(photo_id)
        for face in photo.faces:
            vector_service.remove_face(face.id)
        
        # Delete files
        photo_path = settings.photos_dir / photo.filename
        thumbnail_path = settings.thumbnails_dir / photo.filename
        
        if photo_path.exists():
            os.remove(photo_path)
        if thumbnail_path.exists():
            os.remove(thumbnail_path)
        
        # Delete from database (cascades to detections and faces)
        await db.delete(photo)
        await db.commit()
        
        vector_service.save_all()
        
        return True
    
    async def get_photo_image(self, photo_id: str) -> Optional[Tuple[bytes, str]]:
        """Get photo image bytes and mime type."""
        # We need to look up the filename from DB
        async with settings.database_url:
            pass  # This would need a proper implementation
        
        # For now, search in photos directory
        for photo_path in settings.photos_dir.iterdir():
            if photo_path.stem.endswith(photo_id[:8]):  # Rough match
                async with aiofiles.open(photo_path, 'rb') as f:
                    content = await f.read()
                mime_type = get_mime_type(photo_path.name)
                return content, mime_type
        
        return None
    
    async def update_favorite(
        self, 
        db: AsyncSession, 
        photo_id: str, 
        is_favorite: bool
    ) -> Optional[Photo]:
        """Update photo favorite status."""
        photo = await self.get_photo(db, photo_id)
        if photo:
            photo.is_favorite = is_favorite
            await db.commit()
        return photo
    
    async def get_stats(self, db: AsyncSession) -> GalleryStats:
        """Get gallery statistics."""
        # Total photos
        result = await db.execute(select(func.count(Photo.id)))
        total_photos = result.scalar() or 0
        
        # Total faces
        result = await db.execute(select(func.count(Face.id)))
        total_faces = result.scalar() or 0
        
        # Total people (clusters)
        result = await db.execute(select(func.count(Cluster.id)))
        total_people = result.scalar() or 0
        
        # Total detections
        result = await db.execute(select(func.count(Detection.id)))
        total_objects = result.scalar() or 0
        
        # Categories count
        result = await db.execute(
            select(Detection.class_name, func.count(Detection.id))
            .group_by(Detection.class_name)
        )
        categories = {row[0]: row[1] for row in result.all()}
        
        # Storage used
        result = await db.execute(select(func.sum(Photo.file_size)))
        storage_used = result.scalar() or 0
        
        return GalleryStats(
            total_photos=total_photos,
            total_faces=total_faces,
            total_people=total_people,
            total_objects=total_objects,
            categories=categories,
            storage_used=storage_used,
        )
    
    async def get_categories(self, db: AsyncSession) -> List[CategoryResponse]:
        """Get all object categories with counts."""
        result = await db.execute(
            select(
                Detection.class_name,
                func.count(Detection.id).label('count'),
                # Use group_concat for SQLite compatibility (instead of array_agg)
                func.group_concat(Detection.photo_id.distinct()).label('photo_ids')
            )
            .group_by(Detection.class_name)
            .order_by(func.count(Detection.id).desc())
        )
        
        categories = []
        for row in result.all():
            # group_concat returns comma-separated string, so we split it
            photo_ids_str = row[2]
            photo_ids = photo_ids_str.split(',') if photo_ids_str else []
            
            categories.append(CategoryResponse(
                name=row[0],
                count=row[1],
                photo_ids=photo_ids,
            ))
        
        return categories
    
    async def get_clusters(self, db: AsyncSession) -> List[Cluster]:
        """Get all face clusters."""
        result = await db.execute(
            select(Cluster)
            .options(selectinload(Cluster.faces))
            .order_by(Cluster.created_at.desc())
        )
        return result.scalars().all()


# Global instance
photo_service = PhotoService()