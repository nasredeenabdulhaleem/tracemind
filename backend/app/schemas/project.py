"""Project Pydantic schemas"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    repo_url: Optional[str] = Field(None, max_length=500, description="Repository URL (GitHub)")
    repo_type: Optional[str] = Field(None, description="Repository type: 'github' or 'zip'")
    
    @validator('repo_type')
    def validate_repo_type(cls, v):
        if v and v not in ['github', 'zip']:
            raise ValueError("repo_type must be 'github' or 'zip'")
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    repo_url: Optional[str] = Field(None, max_length=500)
    indexing_status: Optional[str] = Field(None, max_length=50)
    
    @validator('indexing_status')
    def validate_indexing_status(cls, v):
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        if v and v not in valid_statuses:
            raise ValueError(f"indexing_status must be one of: {', '.join(valid_statuses)}")
        return v


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: UUID
    user_id: UUID
    repo_url: Optional[str]
    repo_type: Optional[str]
    r2_object_key: Optional[str]
    is_indexed: bool
    indexing_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    """Schema for project list item (minimal data)"""
    id: UUID
    name: str
    description: Optional[str]
    repo_type: Optional[str]
    is_indexed: bool
    indexing_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectList(BaseModel):
    """Schema for paginated project list"""
    projects: list[ProjectListItem]
    total: int
    page: int = 1
    page_size: int = 20

# Made with Bob