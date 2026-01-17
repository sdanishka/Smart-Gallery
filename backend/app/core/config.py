"""
Smart Gallery Backend - Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # App Info
    app_name: str = "Smart Gallery API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # ML Settings
    device: str = "cuda"  # cuda or cpu
    yolo_model_path: Optional[str] = None
    yolo_confidence: float = 0.25
    face_det_thresh: float = 0.5
    face_sim_thresh: float = 0.6
    clip_model: str = "ViT-L-14"
    clip_pretrained: str = "openai"
    
    # Image Processing
    thumbnail_size: tuple = (400, 400)
    max_image_size: int = 4096
    jpeg_quality: int = 85
    
    # CORS
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def base_dir(self) -> Path:
        return Path(__file__).parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        path = self.base_dir / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def photos_dir(self) -> Path:
        path = self.data_dir / "photos"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def thumbnails_dir(self) -> Path:
        path = self.data_dir / "thumbnails"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def embeddings_dir(self) -> Path:
        path = self.data_dir / "embeddings"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.data_dir}/gallery.db"


# Global settings instance
settings = Settings()