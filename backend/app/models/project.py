"""Project model"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Project(Base):
    """Project model for managing code repositories"""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    repo_url = Column(String(500), nullable=True)
    repo_type = Column(String(20), nullable=True)  # 'github' or 'zip'
    r2_object_key = Column(String(500), nullable=True)
    is_indexed = Column(Boolean, default=False, nullable=False)
    indexing_status = Column(String(50), default="pending", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    code_chunks = relationship("CodeChunk", back_populates="project", cascade="all, delete-orphan")
    analyses = relationship("AnalysisHistory", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, user_id={self.user_id})>"

# Made with Bob
