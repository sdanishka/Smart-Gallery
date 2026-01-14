"""
Smart Gallery Backend - ML Services
Handles YOLO, InsightFace, and CLIP model loading and inference.
"""
import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import cv2
from PIL import Image
import io
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class MLService:
    """Unified ML service for all AI models."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if MLService._initialized:
            return
        
        self.device = settings.device
        self.yolo_model = None
        self.face_app = None
        self.clip_model = None
        self.clip_preprocess = None
        self.clip_tokenizer = None
        
        MLService._initialized = True
    
    async def initialize(self):
        """Initialize all ML models."""
        logger.info("Initializing ML models...")
        
        # Check device availability
        if self.device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"
        
        await self._load_yolo()
        await self._load_insightface()
        await self._load_clip()
        
        logger.info("All ML models initialized successfully")
    
    async def _load_yolo(self):
        """Load YOLO model for object detection."""
        try:
            from ultralytics import YOLO
            
            model_path = settings.yolo_model_path
            if model_path and Path(model_path).exists():
                logger.info(f"Loading custom YOLO model from {model_path}")
                self.yolo_model = YOLO(model_path)
            else:
                logger.info("Loading default YOLOv8x model")
                self.yolo_model = YOLO("yolov8x.pt")
            
            # Warm up
            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
            self.yolo_model(dummy, verbose=False)
            
            logger.info("✅ YOLO model loaded")
        except Exception as e:
            logger.error(f"Failed to load YOLO: {e}")
            raise
    
    async def _load_insightface(self):
        """Load InsightFace for face detection and recognition."""
        try:
            from insightface.app import FaceAnalysis
            
            self.face_app = FaceAnalysis(
                name="buffalo_l",
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider'] 
                if self.device == "cuda" else ['CPUExecutionProvider']
            )
            self.face_app.prepare(ctx_id=0 if self.device == "cuda" else -1, det_size=(640, 640))
            
            logger.info("✅ InsightFace model loaded")
        except Exception as e:
            logger.error(f"Failed to load InsightFace: {e}")
            raise
    
    async def _load_clip(self):
        """Load CLIP model for semantic search."""
        try:
            import open_clip
            
            self.clip_model, _, self.clip_preprocess = open_clip.create_model_and_transforms(
                settings.clip_model,
                pretrained=settings.clip_pretrained,
                device=self.device
            )
            self.clip_tokenizer = open_clip.get_tokenizer(settings.clip_model)
            self.clip_model.eval()
            
            logger.info("✅ CLIP model loaded")
        except Exception as e:
            logger.error(f"Failed to load CLIP: {e}")
            raise
    
    def detect_objects(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run YOLO object detection on an image.
        
        Args:
            image: BGR numpy array
            
        Returns:
            List of detections with class_name, confidence, and bbox
        """
        if self.yolo_model is None:
            raise RuntimeError("YOLO model not initialized")
        
        results = self.yolo_model(image, conf=settings.yolo_confidence, verbose=False)
        
        detections = []
        h, w = image.shape[:2]
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for i in range(len(boxes)):
                box = boxes[i]
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy()
                
                # Normalize coordinates
                x1, y1, x2, y2 = xyxy
                detections.append({
                    "class_name": result.names[cls_id],
                    "confidence": conf,
                    "bbox": {
                        "x1": float(x1 / w),
                        "y1": float(y1 / h),
                        "x2": float(x2 / w),
                        "y2": float(y2 / h),
                    }
                })
        
        return detections
    
    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run face detection and recognition on an image.
        
        Args:
            image: BGR numpy array
            
        Returns:
            List of faces with bbox, embedding, age, gender
        """
        if self.face_app is None:
            raise RuntimeError("InsightFace model not initialized")
        
        # InsightFace expects BGR
        faces = self.face_app.get(image)
        
        h, w = image.shape[:2]
        results = []
        
        for face in faces:
            bbox = face.bbox
            
            # Normalize coordinates
            x1, y1, x2, y2 = bbox
            
            result = {
                "confidence": float(face.det_score),
                "bbox": {
                    "x1": float(max(0, x1) / w),
                    "y1": float(max(0, y1) / h),
                    "x2": float(min(w, x2) / w),
                    "y2": float(min(h, y2) / h),
                },
                "embedding": face.embedding.astype(np.float32) if face.embedding is not None else None,
            }
            
            # Age and gender if available
            if hasattr(face, 'age') and face.age is not None:
                result["age"] = int(face.age)
            if hasattr(face, 'gender') and face.gender is not None:
                result["gender"] = "male" if face.gender == 1 else "female"
            
            results.append(result)
        
        return results
    
    def get_clip_image_embedding(self, image: np.ndarray) -> np.ndarray:
        """
        Get CLIP embedding for an image.
        
        Args:
            image: BGR numpy array
            
        Returns:
            Normalized embedding vector (float32)
        """
        if self.clip_model is None:
            raise RuntimeError("CLIP model not initialized")
        
        # Convert BGR to RGB PIL Image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Preprocess and get embedding
        with torch.no_grad():
            image_input = self.clip_preprocess(pil_image).unsqueeze(0).to(self.device)
            embedding = self.clip_model.encode_image(image_input)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        
        return embedding.cpu().numpy().astype(np.float32).flatten()
    
    def get_clip_text_embedding(self, text: str) -> np.ndarray:
        """
        Get CLIP embedding for text.
        
        Args:
            text: Search query string
            
        Returns:
            Normalized embedding vector (float32)
        """
        if self.clip_model is None:
            raise RuntimeError("CLIP model not initialized")
        
        with torch.no_grad():
            text_tokens = self.clip_tokenizer([text]).to(self.device)
            embedding = self.clip_model.encode_text(text_tokens)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        
        return embedding.cpu().numpy().astype(np.float32).flatten()
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings."""
        embedding1 = embedding1.flatten()
        embedding2 = embedding2.flatten()
        
        # Normalize
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))


# Global ML service instance
ml_service = MLService()
