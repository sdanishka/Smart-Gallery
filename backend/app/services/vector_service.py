"""
Smart Gallery Backend - Vector Search Service
Handles FAISS index management for fast similarity search.
"""
import numpy as np
import faiss
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import pickle
import logging
from threading import Lock

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorIndex:
    """FAISS-based vector index for similarity search."""
    
    def __init__(self, dimension: int, index_path: Path, id_map_path: Path):
        self.dimension = dimension
        self.index_path = index_path
        self.id_map_path = id_map_path
        self.index: Optional[faiss.Index] = None
        self.id_map: List[str] = []  # Maps FAISS index to photo/face IDs
        self.lock = Lock()
        
        self._load_or_create()
    
    def _load_or_create(self):
        """Load existing index or create new one."""
        if self.index_path.exists() and self.id_map_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.id_map_path, 'rb') as f:
                    self.id_map = pickle.load(f)
                logger.info(f"Loaded index with {self.index.ntotal} vectors")
                return
            except Exception as e:
                logger.warning(f"Failed to load index: {e}, creating new")
        
        # Create new index - using IndexFlatIP for cosine similarity (with normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_map = []
        logger.info(f"Created new index with dimension {self.dimension}")
    
    def save(self):
        """Persist index to disk."""
        with self.lock:
            try:
                faiss.write_index(self.index, str(self.index_path))
                with open(self.id_map_path, 'wb') as f:
                    pickle.dump(self.id_map, f)
                logger.debug(f"Saved index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Failed to save index: {e}")
    
    def add(self, id: str, embedding: np.ndarray):
        """Add a single embedding to the index."""
        with self.lock:
            # Normalize for cosine similarity
            embedding = embedding.astype(np.float32).reshape(1, -1)
            faiss.normalize_L2(embedding)
            
            self.index.add(embedding)
            self.id_map.append(id)
    
    def add_batch(self, ids: List[str], embeddings: np.ndarray):
        """Add multiple embeddings to the index."""
        with self.lock:
            embeddings = embeddings.astype(np.float32)
            if len(embeddings.shape) == 1:
                embeddings = embeddings.reshape(1, -1)
            
            faiss.normalize_L2(embeddings)
            
            self.index.add(embeddings)
            self.id_map.extend(ids)
    
    def remove(self, id: str) -> bool:
        """
        Remove an embedding by ID.
        Note: FAISS IndexFlatIP doesn't support removal, so we rebuild.
        """
        with self.lock:
            if id not in self.id_map:
                return False
            
            idx = self.id_map.index(id)
            
            # Get all vectors except the one to remove
            if self.index.ntotal <= 1:
                self.index = faiss.IndexFlatIP(self.dimension)
                self.id_map = []
                return True
            
            # Reconstruct all vectors
            all_vectors = np.zeros((self.index.ntotal, self.dimension), dtype=np.float32)
            for i in range(self.index.ntotal):
                all_vectors[i] = self.index.reconstruct(i)
            
            # Remove the vector
            new_vectors = np.delete(all_vectors, idx, axis=0)
            new_ids = self.id_map[:idx] + self.id_map[idx+1:]
            
            # Rebuild index
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(new_vectors)
            self.id_map = new_ids
            
            return True
    
    def search(self, query: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for similar vectors.
        
        Args:
            query: Query embedding
            k: Number of results
            
        Returns:
            List of (id, similarity) tuples
        """
        with self.lock:
            if self.index.ntotal == 0:
                return []
            
            query = query.astype(np.float32).reshape(1, -1)
            faiss.normalize_L2(query)
            
            k = min(k, self.index.ntotal)
            similarities, indices = self.index.search(query, k)
            
            results = []
            for sim, idx in zip(similarities[0], indices[0]):
                if idx >= 0 and idx < len(self.id_map):
                    results.append((self.id_map[idx], float(sim)))
            
            return results
    
    def get_embedding(self, id: str) -> Optional[np.ndarray]:
        """Get embedding by ID."""
        with self.lock:
            if id not in self.id_map:
                return None
            
            idx = self.id_map.index(id)
            return self.index.reconstruct(idx)
    
    @property
    def count(self) -> int:
        """Number of vectors in index."""
        return self.index.ntotal if self.index else 0


class VectorSearchService:
    """Manages vector indices for different embedding types."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        embeddings_dir = settings.embeddings_dir
        
        # CLIP embeddings (768-dim for ViT-L-14)
        self.clip_index = VectorIndex(
            dimension=768,
            index_path=embeddings_dir / "clip_index.faiss",
            id_map_path=embeddings_dir / "clip_id_map.pkl"
        )
        
        # Face embeddings (512-dim for InsightFace)
        self.face_index = VectorIndex(
            dimension=512,
            index_path=embeddings_dir / "face_index.faiss",
            id_map_path=embeddings_dir / "face_id_map.pkl"
        )
        
        self._initialized = True
        logger.info("Vector search service initialized")
    
    def add_clip_embedding(self, photo_id: str, embedding: np.ndarray):
        """Add CLIP embedding for a photo."""
        self.clip_index.add(photo_id, embedding)
    
    def add_face_embedding(self, face_id: str, embedding: np.ndarray):
        """Add face embedding."""
        self.face_index.add(face_id, embedding)
    
    def remove_photo(self, photo_id: str):
        """Remove all embeddings for a photo."""
        self.clip_index.remove(photo_id)
    
    def remove_face(self, face_id: str):
        """Remove face embedding."""
        self.face_index.remove(face_id)
    
    def search_by_clip(self, query_embedding: np.ndarray, k: int = 20) -> List[Tuple[str, float]]:
        """Search photos by CLIP embedding similarity."""
        return self.clip_index.search(query_embedding, k)
    
    def search_by_face(self, query_embedding: np.ndarray, k: int = 20) -> List[Tuple[str, float]]:
        """Search faces by embedding similarity."""
        return self.face_index.search(query_embedding, k)
    
    def find_similar_faces(self, face_id: str, k: int = 20) -> List[Tuple[str, float]]:
        """Find faces similar to a given face."""
        embedding = self.face_index.get_embedding(face_id)
        if embedding is None:
            return []
        return self.face_index.search(embedding, k + 1)[1:]  # Exclude self
    
    def save_all(self):
        """Persist all indices to disk."""
        self.clip_index.save()
        self.face_index.save()
        logger.info("All vector indices saved")


# Global instance
vector_service = VectorSearchService()
