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
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = Field(default=None, env="DATA_DIR")
    photos_dir: Path = Field(default=None, env="PHOTOS_DIR")
    thumbnails_dir: Path = Field(default=None, env="THUMBNAILS_DIR")
    embeddings_dir: Path = Field(default=None, env="EMBEDDINGS_DIR")
    
    # Database
    database_url: str = Field(default=None, env="DATABASE_URL")
    
    # Model Paths (for custom trained models)
    yolo_model_path: Optional[str] = Field(default=None, env="YOLO_MODEL_PATH")
    
    # ML Settings
    device: str = Field(default="cuda", env="DEVICE")  # cuda or cpu
    yolo_confidence: float = Field(default=0.25, env="YOLO_CONFIDENCE")
    face_det_thresh: float = Field(default=0.5, env="FACE_DET_THRESH")
    face_sim_thresh: float = Field(default=0.6, env="FACE_SIM_THRESH")
    clip_model: str = Field(default="ViT-L-14", env="CLIP_MODEL")
    clip_pretrained: str = Field(default="openai", env="CLIP_PRETRAINED")
    
    # Image Processing
    thumbnail_size: tuple = (400, 400)
    max_image_size: int = 4096  # Max dimension for processing
    jpeg_quality: int = 85
    
    # CORS
    cors_origins: list = ["*"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set default paths if not provided
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        if self.photos_dir is None:
            self.photos_dir = self.data_dir / "photos"
        if self.thumbnails_dir is None:
            self.thumbnails_dir = self.data_dir / "thumbnails"
        if self.embeddings_dir is None:
            self.embeddings_dir = self.data_dir / "embeddings"
        if self.database_url is None:
            self.database_url = f"sqlite+aiosqlite:///{self.data_dir}/gallery.db"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
