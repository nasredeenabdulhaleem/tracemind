"""Code parsing API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.services.project_service import ProjectService
from app.services.storage_service import RepoStorageService
from app.services.parser_service import CodeParserService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{project_id}/parse", status_code=status.HTTP_202_ACCEPTED)
async def parse_project(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Parse project repository and create code chunks
    
    This endpoint triggers background parsing of the repository.
    The parsing process downloads the repo from R2, parses all supported
    files, creates chunks, and stores them in the database.
    
    Args:
        project_id: Project UUID
        background_tasks: FastAPI background tasks
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Status message
        
    Raises:
        HTTPException: If project not found or no repository
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    # Check if project has a repository
    if not project.r2_object_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No repository found for this project. Upload a repository first."
        )
    
    # Check if already parsing
    if project.indexing_status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project is already being parsed"
        )
    
    # Update status to processing
    project.indexing_status = "processing"
    db.commit()
    
    # Add parsing task to background
    background_tasks.add_task(
        parse_project_background,
        str(project_id),
        project.r2_object_key,
        db
    )
    
    logger.info(f"Started parsing for project {project_id}")
    
    return {
        "message": "Parsing started",
        "project_id": str(project_id),
        "status": "processing"
    }


def parse_project_background(project_id: str, r2_object_key: str, db: Session):
    """
    Background task to parse project repository
    
    Args:
        project_id: Project UUID string
        r2_object_key: R2 object key
        db: Database session
    """
    storage_service = RepoStorageService()
    parser_service = CodeParserService()
    temp_dir = None
    
    try:
        logger.info(f"Downloading repository for project {project_id}")
        
        # Download repository from R2
        temp_dir = storage_service.download_repo(r2_object_key)
        
        if not temp_dir:
            raise Exception("Failed to download repository from R2")
        
        logger.info(f"Parsing repository at {temp_dir}")
        
        # Parse repository
        files_parsed, chunks_created = parser_service.parse_repository(
            temp_dir,
            project_id,
            db
        )
        
        # Update project status
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.is_indexed = True
            project.indexing_status = "completed"
            db.commit()
        
        logger.info(
            f"Parsing completed for project {project_id}: "
            f"{files_parsed} files, {chunks_created} chunks"
        )
        
    except Exception as e:
        logger.error(f"Parsing failed for project {project_id}: {e}")
        
        # Update project status to failed
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.indexing_status = "failed"
            db.commit()
    
    finally:
        # Cleanup temp directory
        if temp_dir:
            storage_service.cleanup_temp_dir(temp_dir)


@router.get("/{project_id}/parsing-status", status_code=status.HTTP_200_OK)
async def get_parsing_status(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get parsing status and statistics for a project
    
    Args:
        project_id: Project UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Parsing status and statistics
        
    Raises:
        HTTPException: If project not found
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    # Get parsing stats if completed
    stats = None
    if project.is_indexed:
        parser_service = CodeParserService()
        stats = parser_service.get_parsing_stats(str(project_id), db)
    
    return {
        "project_id": str(project_id),
        "is_indexed": project.is_indexed,
        "indexing_status": project.indexing_status,
        "statistics": stats
    }


@router.delete("/{project_id}/chunks", status_code=status.HTTP_200_OK)
async def delete_chunks(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all code chunks for a project
    
    This is useful for re-parsing a project.
    
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
    
    # Delete all chunks
    from app.models.code_chunk import CodeChunk
    deleted_count = db.query(CodeChunk).filter(
        CodeChunk.project_id == project_id
    ).delete()
    
    # Update project status
    project.is_indexed = False
    project.indexing_status = "pending"
    
    db.commit()
    
    logger.info(f"Deleted {deleted_count} chunks for project {project_id}")
    
    return {
        "message": "Code chunks deleted successfully",
        "project_id": str(project_id),
        "chunks_deleted": deleted_count
    }

# Made with Bob