"""Project service for business logic"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from uuid import UUID

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service class for project operations"""
    
    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate, user_id: UUID) -> Project:
        """
        Create a new project
        
        Args:
            db: Database session
            project_data: Project creation data
            user_id: Owner user ID
            
        Returns:
            Created project object
        """
        new_project = Project(
            user_id=user_id,
            name=project_data.name,
            description=project_data.description,
            repo_url=project_data.repo_url,
            repo_type=project_data.repo_type,
            is_indexed=False,
            indexing_status="pending"
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        return new_project
    
    @staticmethod
    def get_project_by_id(db: Session, project_id: UUID, user_id: UUID) -> Optional[Project]:
        """
        Get project by ID (with ownership check)
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID for ownership verification
            
        Returns:
            Project object or None
        """
        return db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_projects(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Project], int]:
        """
        Get all projects for a user with pagination
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (projects list, total count)
        """
        query = db.query(Project).filter(Project.user_id == user_id)
        total = query.count()
        projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
        
        return projects, total
    
    @staticmethod
    def update_project(
        db: Session,
        project_id: UUID,
        user_id: UUID,
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """
        Update project
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID for ownership verification
            project_data: Update data
            
        Returns:
            Updated project or None if not found
        """
        project = ProjectService.get_project_by_id(db, project_id, user_id)
        
        if not project:
            return None
        
        # Update only provided fields
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: UUID, user_id: UUID) -> bool:
        """
        Delete project
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID for ownership verification
            
        Returns:
            True if deleted, False if not found
        """
        project = ProjectService.get_project_by_id(db, project_id, user_id)
        
        if not project:
            return False
        
        db.delete(project)
        db.commit()
        
        return True
    
    @staticmethod
    def verify_project_ownership(db: Session, project_id: UUID, user_id: UUID) -> Project:
        """
        Verify project ownership and return project
        
        Args:
            db: Database session
            project_id: Project ID
            user_id: User ID
            
        Returns:
            Project object
            
        Raises:
            HTTPException: If project not found or access denied
        """
        project = ProjectService.get_project_by_id(db, project_id, user_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        
        return project

# Made with Bob