"""Repository ingestion API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.code_chunk import CodeChunk as CodeChunkModel
from app.services.repo_service import RepoIngestionService
from app.services.storage_service import RepoStorageService
from app.services.project_service import ProjectService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _replace_existing_repo(project: Project, db: Session, project_id: UUID) -> None:
    """Atomically clear all stale data when replacing an existing repository."""
    storage_service = RepoStorageService()
    if project.r2_object_key:
        storage_service.delete_repo(project.r2_object_key)
    # Clear stale code chunks (re-parse will recreate them)
    db.query(CodeChunkModel).filter(CodeChunkModel.project_id == project_id).delete(synchronize_session=False)
    project.r2_object_key = None
    project.is_indexed = False
    project.indexing_status = "pending"
    db.commit()
    logger.info(f"Cleared existing repo data for project {project_id}")


@router.post("/{project_id}/connect-github", status_code=status.HTTP_200_OK)
async def connect_github_repo(
    project_id: UUID,
    repo_url: str = Form(..., description="GitHub repository URL"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect and ingest a GitHub repository
    
    Args:
        project_id: Project UUID
        repo_url: GitHub repository URL
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message with ingestion details
        
    Raises:
        HTTPException: If project not found or ingestion fails
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)

    # If project already has a repo, atomically replace it
    if project.r2_object_key:
        _replace_existing_repo(project, db, project_id)

    # Ingest repository
    repo_service = RepoIngestionService()
    success, object_key, error = await repo_service.ingest_github_repo(
        repo_url,
        str(current_user.id),
        str(project_id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to ingest GitHub repository"
        )
    
    # Update project
    project.repo_url = repo_url
    project.repo_type = "github"
    project.r2_object_key = object_key
    project.indexing_status = "pending"
    
    db.commit()
    db.refresh(project)
    
    logger.info(f"GitHub repo connected for project {project_id}")
    
    return {
        "message": "GitHub repository connected successfully",
        "project_id": str(project_id),
        "repo_url": repo_url,
        "status": "pending_indexing"
    }


@router.post("/{project_id}/upload-zip", status_code=status.HTTP_200_OK)
async def upload_zip_repo(
    project_id: UUID,
    file: UploadFile = File(..., description="ZIP file containing repository"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a ZIP file containing repository code
    
    Args:
        project_id: Project UUID
        file: ZIP file upload
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message with upload details
        
    Raises:
        HTTPException: If project not found or upload fails
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)

    # If project already has a repo, atomically replace it
    if project.r2_object_key:
        _replace_existing_repo(project, db, project_id)

    # Ingest ZIP file
    repo_service = RepoIngestionService()
    success, object_key, error = await repo_service.ingest_zip_upload(
        file,
        str(current_user.id),
        str(project_id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to process ZIP file"
        )
    
    # Update project
    project.repo_type = "zip"
    project.r2_object_key = object_key
    project.indexing_status = "pending"
    
    db.commit()
    db.refresh(project)
    
    logger.info(f"ZIP uploaded for project {project_id}")
    
    return {
        "message": "ZIP file uploaded successfully",
        "project_id": str(project_id),
        "filename": file.filename,
        "status": "pending_indexing"
    }


@router.delete("/{project_id}/repository", status_code=status.HTTP_200_OK)
async def delete_repository(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete repository from project and R2 storage
    
    Args:
        project_id: Project UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If project not found or deletion fails
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    if not project.r2_object_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No repository found for this project"
        )
    
    # Delete from R2
    from app.services.storage_service import RepoStorageService
    storage_service = RepoStorageService()
    
    success = storage_service.delete_repo(project.r2_object_key)
    
    if not success:
        logger.warning(f"Failed to delete R2 object: {project.r2_object_key}")
        # Continue anyway to clean up database
    
    # Update project
    project.repo_url = None
    project.repo_type = None
    project.r2_object_key = None
    project.is_indexed = False
    project.indexing_status = "pending"
    
    db.commit()
    
    logger.info(f"Repository deleted for project {project_id}")
    
    return {
        "message": "Repository deleted successfully",
        "project_id": str(project_id)
    }


@router.get("/{project_id}/repository/status", status_code=status.HTTP_200_OK)
async def get_repository_status(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get repository status for a project
    
    Args:
        project_id: Project UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Repository status information
        
    Raises:
        HTTPException: If project not found
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    if not project.r2_object_key:
        return {
            "has_repository": False,
            "status": "no_repository"
        }
    
    # Get repo size from R2
    from app.services.storage_service import RepoStorageService
    storage_service = RepoStorageService()
    
    size = storage_service.get_repo_size(project.r2_object_key)
    
    return {
        "has_repository": True,
        "repo_type": project.repo_type,
        "repo_url": project.repo_url,
        "is_indexed": project.is_indexed,
        "indexing_status": project.indexing_status,
        "size_bytes": size,
        "r2_key": project.r2_object_key
    }

# Made with Bob