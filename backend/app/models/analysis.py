"""Analysis history model"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class AnalysisHistory(Base):
    """Analysis history model for storing bug analysis results"""
    
    __tablename__ = "analysis_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bug_description = Column(Text, nullable=False)
    affected_files = Column(JSONB, nullable=True)
    root_cause = Column(Text, nullable=True)
    explanation_simple = Column(Text, nullable=True)
    explanation_technical = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    generated_test = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="analyses")
    
    def __repr__(self):
        return f"<AnalysisHistory(id={self.id}, project_id={self.project_id})>"

# Made with Bob
