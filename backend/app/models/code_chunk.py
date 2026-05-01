"""Code chunk model for storing parsed code segments"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class CodeChunk(Base):
    """Code chunk model for storing parsed and indexed code segments"""
    
    __tablename__ = "code_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True)
    chunk_type = Column(String(50), nullable=True)  # 'function', 'class', 'file'
    embedding_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="code_chunks")
    
    def __repr__(self):
        return f"<CodeChunk(id={self.id}, file={self.file_path}, project_id={self.project_id})>"

# Made with Bob
