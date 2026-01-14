"""
Smart Gallery Backend - Clusters (People) API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import logging

from app.core.database import get_db
from app.models.database import Cluster, Face
from app.models.schemas import ClusterResponse, ClusterUpdate, PhotoResponse
from app.services.photo_service import photo_service
from app.services.clustering_service import clustering_service
from app.services.search_service import search_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clusters", tags=["People/Clusters"])


@router.get("", response_model=List[ClusterResponse])
async def list_clusters(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all face clusters (people).
    
    Each cluster represents a unique person detected across photos.
    """
    clusters = await photo_service.get_clusters(db)
    return [ClusterResponse(**c.to_dict()) for c in clusters]


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(
    cluster_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific cluster by ID."""
    result = await db.execute(
        select(Cluster).where(Cluster.id == cluster_id)
    )
    cluster = result.scalar_one_or_none()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    return ClusterResponse(**cluster.to_dict())


@router.patch("/{cluster_id}", response_model=ClusterResponse)
async def update_cluster(
    cluster_id: str,
    update: ClusterUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update cluster name (assign a name to a person)."""
    result = await db.execute(
        select(Cluster).where(Cluster.id == cluster_id)
    )
    cluster = result.scalar_one_or_none()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    cluster.name = update.name
    await db.commit()
    
    # Reload with relationships
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Cluster)
        .options(selectinload(Cluster.faces))
        .where(Cluster.id == cluster_id)
    )
    cluster = result.scalar_one()
    
    return ClusterResponse(**cluster.to_dict())


@router.get("/{cluster_id}/photos", response_model=List[PhotoResponse])
async def get_cluster_photos(
    cluster_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get all photos containing faces from this cluster (person)."""
    photos = await search_service.search_by_person(db, cluster_id, limit)
    return [PhotoResponse(**p.to_dict()) for p in photos]


@router.post("/{cluster_id}/merge/{other_cluster_id}")
async def merge_clusters(
    cluster_id: str,
    other_cluster_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Merge two clusters into one.
    
    Use this when the same person has been split into multiple clusters.
    All faces from other_cluster_id will be moved to cluster_id.
    """
    # Verify both clusters exist
    result = await db.execute(
        select(Cluster).where(Cluster.id == cluster_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Target cluster not found")
    
    result = await db.execute(
        select(Cluster).where(Cluster.id == other_cluster_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Source cluster not found")
    
    merged_id = await clustering_service.merge_clusters(db, cluster_id, other_cluster_id)
    
    return {"success": True, "merged_cluster_id": merged_id}


@router.post("/{cluster_id}/faces/{face_id}/remove")
async def remove_face_from_cluster(
    cluster_id: str,
    face_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Remove a face from a cluster and create a new cluster for it.
    
    Use this when a face has been incorrectly grouped with the wrong person.
    """
    # Verify the face belongs to this cluster
    result = await db.execute(
        select(Face).where(Face.id == face_id, Face.cluster_id == cluster_id)
    )
    face = result.scalar_one_or_none()
    
    if not face:
        raise HTTPException(
            status_code=404, 
            detail="Face not found or doesn't belong to this cluster"
        )
    
    new_cluster_id = await clustering_service.split_face_to_new_cluster(db, face_id)
    await db.commit()
    
    return {"success": True, "new_cluster_id": new_cluster_id}


@router.post("/recluster")
async def trigger_reclustering(
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a full reclustering of all faces.
    
    This will clear all existing clusters and re-cluster all faces.
    Use this after changing clustering thresholds or to fix clustering issues.
    """
    await clustering_service.recluster_all(db)
    
    clusters = await photo_service.get_clusters(db)
    
    return {
        "success": True,
        "message": "Reclustering complete",
        "cluster_count": len(clusters),
    }
