"""Analysis orchestration service - coordinates all AI agents"""

from typing import Dict, Any
import time
import logging
from sqlalchemy.orm import Session

from app.agents import (
    BugUnderstandingAgent,
    CodeRetrievalAgent,
    RootCauseAgent,
    FixGeneratorAgent,
    TestGeneratorAgent
)
from app.services.vector_service import VectorIndexService
from app.models.analysis import AnalysisHistory

logger = logging.getLogger(__name__)


class AnalysisOrchestrationService:
    """Service for orchestrating bug analysis pipeline"""
    
    def __init__(self):
        """Initialize all agents"""
        self.bug_understanding_agent = BugUnderstandingAgent()
        self.code_retrieval_agent = CodeRetrievalAgent()
        self.root_cause_agent = RootCauseAgent()
        self.fix_generator_agent = FixGeneratorAgent()
        self.test_generator_agent = TestGeneratorAgent()
        self.vector_service = VectorIndexService()
    
    def analyze_bug(
        self,
        bug_description: str,
        project_id: str,
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Run complete bug analysis pipeline
        
        Args:
            bug_description: User's bug description
            project_id: Project UUID
            user_id: User UUID
            db: Database session
            
        Returns:
            Complete analysis results
        """
        start_time = time.time()
        
        try:
            # Step 1: Bug Understanding
            logger.info("Step 1: Understanding bug...")
            bug_info = self.bug_understanding_agent.process(bug_description)
            
            # Step 2: Code Retrieval
            logger.info("Step 2: Retrieving relevant code...")
            search_results = self.vector_service.search_similar(
                project_id,
                bug_info.get("summary", bug_description),
                top_k=5,
                db=db
            )
            
            # Get full content for chunks
            for result in search_results:
                content = self.vector_service.get_chunk_content(result["chunk_id"], db)
                result["content"] = content or ""
            
            retrieval_result = self.code_retrieval_agent.process(bug_info, search_results)
            relevant_chunks = retrieval_result["relevant_chunks"]
            
            # Step 3: Root Cause Analysis
            logger.info("Step 3: Analyzing root cause...")
            root_cause_result = self.root_cause_agent.process(bug_info, relevant_chunks)
            
            # Step 4: Fix Generation
            logger.info("Step 4: Generating fix...")
            # Use first relevant chunk as affected code
            affected_code = relevant_chunks[0]["content"] if relevant_chunks else ""
            fix_result = self.fix_generator_agent.process(
                bug_info,
                root_cause_result,
                affected_code
            )
            
            # Step 5: Test Generation
            logger.info("Step 5: Generating test...")
            language = relevant_chunks[0]["language"] if relevant_chunks else "python"
            test_result = self.test_generator_agent.process(
                bug_info,
                fix_result["suggested_fix"],
                language
            )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Prepare result
            result = {
                "bug_description": bug_description,
                "bug_summary": bug_info.get("summary", ""),
                "affected_components": bug_info.get("affected_components", []),
                "bug_type": bug_info.get("bug_type", "unknown"),
                "severity": bug_info.get("severity", "medium"),
                "relevant_files": [chunk["file_path"] for chunk in relevant_chunks],
                "code_chunks": relevant_chunks,
                "root_cause": root_cause_result.get("root_cause", ""),
                "explanation_technical": root_cause_result.get("explanation", ""),
                "suggested_fix": fix_result.get("suggested_fix", ""),
                "explanation_simple": fix_result.get("explanation", ""),
                "generated_test": test_result.get("generated_test", ""),
                "test_framework": test_result.get("test_framework", "pytest"),
                "processing_time_ms": processing_time_ms
            }
            
            # Store in database
            analysis = self._store_analysis(result, project_id, user_id, db)
            result["analysis_id"] = str(analysis.id)
            result["created_at"] = analysis.created_at
            
            logger.info(f"Analysis complete in {processing_time_ms}ms")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _store_analysis(
        self,
        result: Dict[str, Any],
        project_id: str,
        user_id: str,
        db: Session
    ) -> AnalysisHistory:
        """
        Store analysis results in database
        
        Args:
            result: Analysis results
            project_id: Project UUID
            user_id: User UUID
            db: Database session
            
        Returns:
            Created AnalysisHistory object
        """
        analysis = AnalysisHistory(
            project_id=project_id,
            user_id=user_id,
            bug_description=result["bug_description"],
            affected_files=result["relevant_files"],
            root_cause=result["root_cause"],
            explanation_simple=result["explanation_simple"],
            explanation_technical=result["explanation_technical"],
            suggested_fix=result["suggested_fix"],
            generated_test=result["generated_test"],
            processing_time_ms=result["processing_time_ms"]
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return analysis
    
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