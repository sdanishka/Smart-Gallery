"""
Smart Gallery Backend - Database Models
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, LargeBinary, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Photo(Base):
    """Photo model storing image metadata and AI analysis results."""
    __tablename__ = "photos"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False, unique=True)
    original_filename = Column(String(255), nullable=False)
    
    # File info
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(50), nullable=False)
    width = Column(Integer)
    height = Column(Integer)
    
    # Timestamps
    upload_date = Column(DateTime, default=func.now(), nullable=False)
    taken_date = Column(DateTime)  # From EXIF
    
    # EXIF data
    exif_data = Column(JSON)
    
    # AI Processing status
    processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    # CLIP embedding stored as binary (numpy array bytes)
    clip_embedding = Column(LargeBinary)
    
    # Relationships
    detections = relationship("Detection", back_populates="photo", cascade="all, delete-orphan")
    faces = relationship("Face", back_populates="photo", cascade="all, delete-orphan")
    
    # Favorites
    is_favorite = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "taken_date": self.taken_date.isoformat() if self.taken_date else None,
            "is_favorite": self.is_favorite,
            "detections": [d.to_dict() for d in self.detections],
            "faces": [f.to_dict() for f in self.faces],
            "has_clip_embedding": self.clip_embedding is not None,
        }


class Detection(Base):
    """YOLO object detection results."""
    __tablename__ = "detections"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    photo_id = Column(String(36), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    
    # Detection info
    class_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Bounding box (normalized 0-1)
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    
    # Relationship
    photo = relationship("Photo", back_populates="detections")
    
    def to_dict(self):
        return {
            "id": self.id,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bbox": {
                "x1": self.bbox_x1,
                "y1": self.bbox_y1,
                "x2": self.bbox_x2,
                "y2": self.bbox_y2,
            }
        }


class Face(Base):
    """Face detection and recognition results."""
    __tablename__ = "faces"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    photo_id = Column(String(36), ForeignKey("photos.id", ondelete="CASCADE"), nullable=False)
    cluster_id = Column(String(36), ForeignKey("clusters.id", ondelete="SET NULL"))
    
    # Detection info
    confidence = Column(Float, nullable=False)
    
    # Bounding box (normalized 0-1)
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    
    # Face attributes
    age = Column(Integer)
    gender = Column(String(10))  # 'male' or 'female'
    
    # Face embedding (512-dim vector as binary)
    embedding = Column(LargeBinary)
    
    # Relationships
    photo = relationship("Photo", back_populates="faces")
    cluster = relationship("Cluster", back_populates="faces")
    
    def to_dict(self):
        return {
            "id": self.id,
            "confidence": self.confidence,
            "bbox": {
                "x1": self.bbox_x1,
                "y1": self.bbox_y1,
                "x2": self.bbox_x2,
                "y2": self.bbox_y2,
            },
            "age": self.age,
            "gender": self.gender,
            "cluster_id": self.cluster_id,
        }


class Cluster(Base):
    """Face clusters representing individual people."""
    __tablename__ = "clusters"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100))  # User-assigned name
    
    # Representative face embedding (average or centroid)
    centroid_embedding = Column(LargeBinary)
    
    # Representative photo for display
    representative_photo_id = Column(String(36))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    faces = relationship("Face", back_populates="cluster")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "face_count": len(self.faces),
            "representative_photo_id": self.representative_photo_id,
            "photo_ids": list(set(f.photo_id for f in self.faces)),
        }
