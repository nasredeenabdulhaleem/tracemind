"""Analysis orchestration service - coordinates all AI agents using watsonx Orchestrate"""

from typing import Dict, Any
import logging
from sqlalchemy.orm import Session

from app.services.orchestrate_service import WatsonxOrchestrateService
from app.models.analysis import AnalysisHistory

logger = logging.getLogger(__name__)


class AnalysisOrchestrationService:
    """
    Service for orchestrating bug analysis pipeline using watsonx Orchestrate
    
    This service provides a simplified interface to the watsonx Orchestrate workflow,
    maintaining backward compatibility while leveraging advanced workflow management.
    """
    
    def __init__(self):
        """Initialize watsonx Orchestrate service"""
        self.orchestrate_service = WatsonxOrchestrateService()
        logger.info("Analysis service initialized with watsonx Orchestrate")
    
    def analyze_bug(
        self,
        bug_description: str,
        project_id: str,
        user_id: str,
        db: Session,
        callback: callable = None
    ) -> Dict[str, Any]:
        """
        Run complete bug analysis pipeline using watsonx Orchestrate
        
        Args:
            bug_description: User's bug description
            project_id: Project UUID
            user_id: User UUID
            db: Database session
            callback: Optional callback for progress updates
            
        Returns:
            Complete analysis results with workflow metadata
        """
        logger.info("Starting bug analysis with watsonx Orchestrate")
        
        try:
            # Execute workflow using watsonx Orchestrate
            result = self.orchestrate_service.execute_workflow(
                bug_description=bug_description,
                project_id=project_id,
                user_id=user_id,
                db=db,
                callback=callback
            )
            
            logger.info("Bug analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def get_analysis_history(
        self,
        project_id: str,
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> tuple:
        """
        Get analysis history for a project
        
        Args:
            project_id: Project UUID
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Tuple of (analyses list, total count)
        """
        query = db.query(AnalysisHistory).filter(
            AnalysisHistory.project_id == project_id
        )
        total = query.count()
        analyses = query.order_by(
            AnalysisHistory.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return analyses, total

# Made with Bob