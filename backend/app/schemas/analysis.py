"""Analysis Pydantic schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class AnalysisRequest(BaseModel):
    """Schema for bug analysis request"""
    bug_description: str = Field(..., min_length=10, max_length=5000, description="Bug description")
    project_id: UUID = Field(..., description="Project UUID")


class CodeChunkInfo(BaseModel):
    """Schema for code chunk information"""
    file_path: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    language: Optional[str] = None
    content: str
    relevance_score: Optional[float] = None


class AnalysisResponse(BaseModel):
    """Schema for bug analysis response"""
    analysis_id: UUID
    project_id: UUID
    bug_description: str
    
    # Bug Understanding
    bug_summary: str
    affected_components: List[str]
    bug_type: str
    severity: str
    
    # Code Retrieval
    relevant_files: List[str]
    code_chunks: List[CodeChunkInfo]
    
    # Root Cause
    root_cause: str
    explanation_technical: str
    
    # Fix
    suggested_fix: str
    explanation_simple: str
    fix_explanation: Optional[str] = None
    testing_notes: Optional[str] = None
    
    # Test
    generated_test: str
    test_framework: str
    
    # Metadata
    processing_time_ms: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisListItem(BaseModel):
    """Schema for analysis list item"""
    id: UUID
    project_id: UUID
    bug_description: str
    bug_summary: Optional[str] = None
    severity: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisList(BaseModel):
    """Schema for paginated analysis list"""
    analyses: List[AnalysisListItem]
    total: int
    page: int = 1
    page_size: int = 20

# Made with Bob