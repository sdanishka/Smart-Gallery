"""
Smart Gallery Backend - Face Clustering Service
Groups detected faces into clusters representing individuals.
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
import logging

from app.models.database import Face, Cluster, Photo
from app.core.config import settings
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)


class ClusteringService:
    """Service for clustering faces into person groups."""
    
    def __init__(self):
        self.similarity_threshold = settings.face_sim_thresh
    
    async def assign_face_to_cluster(
        self, 
        db: AsyncSession, 
        face: Face, 
        embedding: np.ndarray
    ) -> Optional[str]:
        """
        Assign a face to an existing cluster or create a new one.
        
        Args:
            db: Database session
            face: Face object to assign
            embedding: Face embedding vector
            
        Returns:
            Cluster ID
        """
        # Search for similar faces
        similar_faces = vector_service.search_by_face(embedding, k=10)
        
        if not similar_faces:
            # Create new cluster
            return await self._create_cluster(db, face, embedding)
        
        # Find the best matching cluster
        best_cluster_id = None
        best_similarity = 0.0
        
        for face_id, similarity in similar_faces:
            if similarity < self.similarity_threshold:
                continue
            
            # Get the face's cluster
            result = await db.execute(
                select(Face.cluster_id).where(Face.id == face_id)
            )
            cluster_id = result.scalar_one_or_none()
            
            if cluster_id and similarity > best_similarity:
                best_cluster_id = cluster_id
                best_similarity = similarity
        
        if best_cluster_id:
            # Assign to existing cluster
            face.cluster_id = best_cluster_id
            await self._update_cluster_centroid(db, best_cluster_id)
            logger.debug(f"Assigned face {face.id} to cluster {best_cluster_id} (sim={best_similarity:.3f})")
            return best_cluster_id
        else:
            # Create new cluster
            return await self._create_cluster(db, face, embedding)
    
    async def _create_cluster(
        self, 
        db: AsyncSession, 
        face: Face, 
        embedding: np.ndarray
    ) -> str:
        """Create a new cluster for a face."""
        cluster = Cluster(
            centroid_embedding=embedding.tobytes(),
            representative_photo_id=face.photo_id,
        )
        db.add(cluster)
        await db.flush()
        
        face.cluster_id = cluster.id
        
        logger.debug(f"Created new cluster {cluster.id} for face {face.id}")
        return cluster.id
    
    async def _update_cluster_centroid(self, db: AsyncSession, cluster_id: str):
        """Update cluster centroid based on all faces in cluster."""
        result = await db.execute(
            select(Face).where(Face.cluster_id == cluster_id)
        )
        faces = result.scalars().all()
        
        if not faces:
            return
        
        # Calculate new centroid
        embeddings = []
        for face in faces:
            if face.embedding:
                embeddings.append(np.frombuffer(face.embedding, dtype=np.float32))
        
        if embeddings:
            centroid = np.mean(embeddings, axis=0).astype(np.float32)
            
            # Update cluster
            await db.execute(
                update(Cluster)
                .where(Cluster.id == cluster_id)
                .values(centroid_embedding=centroid.tobytes())
            )
    
    async def recluster_all(self, db: AsyncSession):
        """
        Recluster all faces from scratch.
        Useful after threshold changes or to optimize clusters.
        """
        logger.info("Starting full face reclustering...")
        
        # Get all faces with embeddings
        result = await db.execute(
            select(Face).where(Face.embedding.isnot(None))
        )
        faces = result.scalars().all()
        
        if not faces:
            logger.info("No faces to cluster")
            return
        
        # Clear existing clusters
        await db.execute(update(Face).values(cluster_id=None))
        result = await db.execute(select(Cluster))
        for cluster in result.scalars().all():
            await db.delete(cluster)
        
        # Rebuild face index
        vector_service.face_index.index = None
        vector_service.face_index._load_or_create()
        
        # Re-add all embeddings and cluster
        for face in faces:
            embedding = np.frombuffer(face.embedding, dtype=np.float32)
            vector_service.add_face_embedding(face.id, embedding)
            await self.assign_face_to_cluster(db, face, embedding)
        
        await db.commit()
        vector_service.save_all()
        
        logger.info(f"Reclustering complete: {len(faces)} faces processed")
    
    async def merge_clusters(
        self, 
        db: AsyncSession, 
        cluster_id_1: str, 
        cluster_id_2: str
    ) -> str:
        """Merge two clusters into one."""
        # Move all faces from cluster 2 to cluster 1
        await db.execute(
            update(Face)
            .where(Face.cluster_id == cluster_id_2)
            .values(cluster_id=cluster_id_1)
        )
        
        # Delete cluster 2
        result = await db.execute(
            select(Cluster).where(Cluster.id == cluster_id_2)
        )
        cluster_2 = result.scalar_one_or_none()
        if cluster_2:
            await db.delete(cluster_2)
        
        # Update cluster 1 centroid
        await self._update_cluster_centroid(db, cluster_id_1)
        
        logger.info(f"Merged cluster {cluster_id_2} into {cluster_id_1}")
        return cluster_id_1
    
    async def split_face_to_new_cluster(
        self, 
        db: AsyncSession, 
        face_id: str
    ) -> str:
        """Move a face to its own new cluster."""
        result = await db.execute(
            select(Face).where(Face.id == face_id)
        )
        face = result.scalar_one_or_none()
        
        if not face or not face.embedding:
            raise ValueError(f"Face {face_id} not found or has no embedding")
        
        old_cluster_id = face.cluster_id
        embedding = np.frombuffer(face.embedding, dtype=np.float32)
        
        # Create new cluster
        new_cluster_id = await self._create_cluster(db, face, embedding)
        
        # Update old cluster centroid
        if old_cluster_id:
            await self._update_cluster_centroid(db, old_cluster_id)
        
        return new_cluster_id
    
    async def get_cluster_photos(
        self, 
        db: AsyncSession, 
        cluster_id: str
    ) -> List[str]:
        """Get all photo IDs containing faces from a cluster."""
        result = await db.execute(
            select(Face.photo_id)
            .where(Face.cluster_id == cluster_id)
            .distinct()
        )
        return [row[0] for row in result.all()]


# Global instance
clustering_service = ClusteringService()
