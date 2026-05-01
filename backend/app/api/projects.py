"""Project management API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListItem,
    ProjectList
)
from app.services.project_service import ProjectService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project
    
    Args:
        project_data: Project creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created project object
    """
    project = ProjectService.create_project(db, project_data, current_user.id)
    return project


@router.get("/", response_model=ProjectList)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects for the current user with pagination
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of projects
    """
    skip = (page - 1) * page_size
    projects, total = ProjectService.get_user_projects(db, current_user.id, skip, page_size)
    
    return ProjectList(
        projects=[ProjectListItem.from_orm(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get project details by ID
    
    Args:
        project_id: Project UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Project details
        
    Raises:
        HTTPException: If project not found or access denied
    """
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project
    
    Args:
        project_id: Project UUID
        project_data: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated project
        
    Raises:
        HTTPException: If project not found or access denied
    """
    project = ProjectService.update_project(db, project_id, current_user.id, project_data)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete project
    
    Args:
        project_id: Project UUID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If project not found or access denied
    """
    deleted = ProjectService.delete_project(db, project_id, current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return None

# Made with Bob