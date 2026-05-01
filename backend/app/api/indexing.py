"""Vector indexing API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.services.project_service import ProjectService
from app.services.vector_service import VectorIndexService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{project_id}/index", status_code=status.HTTP_202_ACCEPTED)
async def create_index(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create FAISS vector index for project code chunks
    
    This endpoint triggers background indexing of all code chunks.
    The project must be parsed before indexing.
    
    Args:
        project_id: Project UUID
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If project not found or not parsed
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    # Check if project is parsed
    if not project.is_indexed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project must be parsed before indexing. Parse the repository first."
        )
    
    # Check if already has index
    vector_service = VectorIndexService()
    if vector_service.index_exists(str(project_id)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Index already exists. Delete it first to recreate."
        )
    
    # Add indexing task to background
    background_tasks.add_task(
        create_index_background,
        str(project_id),
        db
    )
    
    logger.info(f"Started indexing for project {project_id}")
    
    return {
        "message": "Indexing started",
        "project_id": str(project_id),
        "status": "processing"
    }


def create_index_background(project_id: str, db: Session):
    """
    Background task to create vector index
    
    Args:
        project_id: Project UUID string
        db: Database session
    """
    vector_service = VectorIndexService()
    
    try:
        logger.info(f"Creating vector index for project {project_id}")
        
        chunks_indexed, index_path = vector_service.create_index(project_id, db)
        
        logger.info(
            f"Indexing completed for project {project_id}: "
            f"{chunks_indexed} chunks indexed"
        )
        
    except Exception as e:
        logger.error(f"Indexing failed for project {project_id}: {e}")


@router.post("/{project_id}/search", status_code=status.HTTP_200_OK)
async def search_code(
    project_id: UUID,
    query: str,
    top_k: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for similar code chunks using vector similarity
    
    Args:
        project_id: Project UUID
        query: Search query text
        top_k: Number of results to return (default: 5, max: 20)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of similar code chunks with scores
        
    Raises:
        HTTPException: If project not found or not indexed
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    # Validate top_k
    if top_k < 1 or top_k > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="top_k must be between 1 and 20"
        )
    
    # Check if index exists
    vector_service = VectorIndexService()
    if not vector_service.index_exists(str(project_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No index found for this project. Create an index first."
        )
    
    try:
        # Search
        results = vector_service.search_similar(
            str(project_id),
            query,
            top_k,
            db
        )
        
        # Optionally include chunk content
        for result in results:
            content = vector_service.get_chunk_content(result['chunk_id'], db)
            result['content'] = content
        
        return {
            "query": query,
            "project_id": str(project_id),
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{project_id}/index/status", status_code=status.HTTP_200_OK)
async def get_index_status(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get index status and statistics
    
    Args:
        project_id: Project UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Index status and statistics
        
    Raises:
        HTTPException: If project not found
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    vector_service = VectorIndexService()
    
    # Check if index exists
    has_index = vector_service.index_exists(str(project_id))
    
    # Get stats if index exists
    stats = None
    if has_index:
        stats = vector_service.get_index_stats(str(project_id))
    
    return {
        "project_id": str(project_id),
        "has_index": has_index,
        "statistics": stats
    }


@router.delete("/{project_id}/index", status_code=status.HTTP_200_OK)
async def delete_index(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete vector index for a project
    
    Args:
        project_id: Project UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If project not found
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    vector_service = VectorIndexService()
    deleted = vector_service.delete_index(str(project_id))
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No index found for this project"
        )
    
    logger.info(f"Index deleted for project {project_id}")
    
    return {
        "message": "Index deleted successfully",
        "project_id": str(project_id)
    }

# Made with Bob