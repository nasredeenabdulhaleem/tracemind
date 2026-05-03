"""watsonx Orchestrate integration for agent workflow management"""

from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime
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
from app.config import settings

logger = logging.getLogger(__name__)


class WorkflowStep:
    """Represents a single step in the analysis workflow"""
    
    def __init__(self, name: str, agent: Any, dependencies: List[str] = None):
        self.name = name
        self.agent = agent
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, running, completed, failed
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            "name": self.name,
            "status": self.status,
            "dependencies": self.dependencies,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": int((self.end_time - self.start_time).total_seconds() * 1000) if self.end_time and self.start_time else None,
            "error": self.error
        }


class WatsonxOrchestrateService:
    """
    Service for orchestrating bug analysis workflow using watsonx.ai
    
    This service manages the multi-agent workflow for bug analysis,
    providing:
    - Sequential and parallel execution
    - Dependency management
    - Error handling and recovery
    - Progress tracking
    - Result aggregation
    """
    
    def __init__(self):
        """Initialize orchestration service with all agents"""
        self.vector_service = VectorIndexService()
        
        # Initialize workflow steps
        self.workflow_steps = {
            "bug_understanding": WorkflowStep(
                name="Bug Understanding",
                agent=BugUnderstandingAgent(),
                dependencies=[]
            ),
            "code_retrieval": WorkflowStep(
                name="Code Retrieval",
                agent=CodeRetrievalAgent(),
                dependencies=["bug_understanding"]
            ),
            "root_cause_analysis": WorkflowStep(
                name="Root Cause Analysis",
                agent=RootCauseAgent(),
                dependencies=["bug_understanding", "code_retrieval"]
            ),
            "fix_generation": WorkflowStep(
                name="Fix Generation",
                agent=FixGeneratorAgent(),
                dependencies=["bug_understanding", "root_cause_analysis"]
            ),
            "test_generation": WorkflowStep(
                name="Test Generation",
                agent=TestGeneratorAgent(),
                dependencies=["fix_generation"]
            )
        }
        
        logger.info("watsonx Orchestrate Service initialized with 5-agent workflow")
    
    def execute_workflow(
        self,
        bug_description: str,
        project_id: str,
        user_id: str,
        db: Session,
        callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete bug analysis workflow
        
        Args:
            bug_description: User's bug description
            project_id: Project UUID
            user_id: User UUID
            db: Database session
            callback: Optional callback for progress updates
            
        Returns:
            Complete analysis results with workflow metadata
        """
        workflow_start = datetime.now()
        workflow_context = {
            "bug_description": bug_description,
            "project_id": project_id,
            "user_id": user_id
        }
        
        try:
            # Reset workflow state
            self._reset_workflow()
            
            # Execute workflow steps in order
            logger.info("Starting watsonx Orchestrate workflow execution")
            
            # Step 1: Bug Understanding
            bug_info = self._execute_step(
                "bug_understanding",
                workflow_context,
                callback
            )
            workflow_context["bug_info"] = bug_info
            
            # Step 2: Code Retrieval (parallel with vector search)
            search_results = self._perform_vector_search(
                project_id,
                bug_info.get("summary", bug_description),
                db
            )
            workflow_context["search_results"] = search_results
            
            retrieval_result = self._execute_step(
                "code_retrieval",
                workflow_context,
                callback
            )
            workflow_context["relevant_chunks"] = retrieval_result["relevant_chunks"]
            
            # Step 3: Root Cause Analysis
            root_cause_result = self._execute_step(
                "root_cause_analysis",
                workflow_context,
                callback
            )
            workflow_context["root_cause"] = root_cause_result
            
            # Step 4: Fix Generation
            workflow_context["affected_code"] = (
                workflow_context["relevant_chunks"][0]["content"]
                if workflow_context["relevant_chunks"]
                else ""
            )
            fix_result = self._execute_step(
                "fix_generation",
                workflow_context,
                callback
            )
            workflow_context["fix"] = fix_result
            
            # Step 5: Test Generation
            workflow_context["language"] = (
                workflow_context["relevant_chunks"][0]["language"]
                if workflow_context["relevant_chunks"]
                else "python"
            )
            test_result = self._execute_step(
                "test_generation",
                workflow_context,
                callback
            )
            
            # Calculate total workflow time
            workflow_end = datetime.now()
            total_time_ms = int((workflow_end - workflow_start).total_seconds() * 1000)
            
            # Prepare final result
            result = self._prepare_result(
                workflow_context,
                test_result,
                total_time_ms
            )
            
            # Store in database
            analysis = self._store_analysis(result, project_id, user_id, db)
            result["analysis_id"] = str(analysis.id)
            result["created_at"] = analysis.created_at
            
            # Add workflow metadata
            result["workflow"] = {
                "total_time_ms": total_time_ms,
                "steps": [step.to_dict() for step in self.workflow_steps.values()],
                "status": "completed"
            }
            
            logger.info(f"Workflow completed successfully in {total_time_ms}ms")
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            
            # Mark current step as failed
            for step in self.workflow_steps.values():
                if step.status == "running":
                    step.status = "failed"
                    step.error = str(e)
                    step.end_time = datetime.now()
            
            raise
    
    def _execute_step(
        self,
        step_name: str,
        context: Dict[str, Any],
        callback: Optional[callable] = None
    ) -> Any:
        """
        Execute a single workflow step
        
        Args:
            step_name: Name of the step to execute
            context: Workflow context with all data
            callback: Optional progress callback
            
        Returns:
            Step execution result
        """
        step = self.workflow_steps[step_name]
        
        # Check dependencies
        for dep in step.dependencies:
            if self.workflow_steps[dep].status != "completed":
                raise RuntimeError(f"Dependency {dep} not completed for {step_name}")
        
        # Execute step
        step.status = "running"
        step.start_time = datetime.now()
        
        logger.info(f"Executing step: {step.name}")
        
        if callback:
            callback({
                "step": step_name,
                "status": "running",
                "message": f"Executing {step.name}..."
            })
        
        try:
            # Execute based on step type
            if step_name == "bug_understanding":
                result = step.agent.process(context["bug_description"])
            
            elif step_name == "code_retrieval":
                result = step.agent.process(
                    context["bug_info"],
                    context["search_results"]
                )
            
            elif step_name == "root_cause_analysis":
                result = step.agent.process(
                    context["bug_info"],
                    context["relevant_chunks"]
                )
            
            elif step_name == "fix_generation":
                result = step.agent.process(
                    context["bug_info"],
                    context["root_cause"],
                    context["affected_code"]
                )
            
            elif step_name == "test_generation":
                result = step.agent.process(
                    context["bug_info"],
                    context["fix"]["suggested_fix"],
                    context["language"]
                )
            
            else:
                raise ValueError(f"Unknown step: {step_name}")
            
            step.status = "completed"
            step.result = result
            step.end_time = datetime.now()
            
            if callback:
                callback({
                    "step": step_name,
                    "status": "completed",
                    "message": f"{step.name} completed"
                })
            
            return result
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.end_time = datetime.now()
            
            if callback:
                callback({
                    "step": step_name,
                    "status": "failed",
                    "message": f"{step.name} failed: {str(e)}"
                })
            
            raise
    
    def _perform_vector_search(
        self,
        project_id: str,
        query: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Perform vector search for relevant code"""
        search_results = self.vector_service.search_similar(
            project_id,
            query,
            top_k=5,
            db=db
        )
        
        # Get full content for chunks
        for result in search_results:
            content = self.vector_service.get_chunk_content(result["chunk_id"], db)
            result["content"] = content or ""
        
        return search_results
    
    def _prepare_result(
        self,
        context: Dict[str, Any],
        test_result: Dict[str, Any],
        total_time_ms: int
    ) -> Dict[str, Any]:
        """Prepare final analysis result"""
        bug_info = context["bug_info"]
        relevant_chunks = context["relevant_chunks"]
        root_cause = context["root_cause"]
        fix = context["fix"]
        
        # Prefer root cause's simple explanation; fall back to fix agent's then empty
        simple_explanation = (
            root_cause.get("simple_explanation")
            or fix.get("simple_explanation")
            or ""
        )

        return {
            "bug_description": context["bug_description"],
            "bug_summary": bug_info.get("summary", ""),
            "affected_components": bug_info.get("affected_components", []),
            "bug_type": bug_info.get("bug_type", "unknown"),
            "severity": bug_info.get("severity", "medium"),
            "relevant_files": [chunk["file_path"] for chunk in relevant_chunks],
            "code_chunks": relevant_chunks,
            "root_cause": root_cause.get("root_cause", ""),
            "explanation_technical": root_cause.get("explanation", ""),
            "explanation_simple": simple_explanation,
            "suggested_fix": fix.get("suggested_fix", ""),
            "fix_explanation": fix.get("explanation", ""),
            "testing_notes": fix.get("testing_notes", ""),
            "generated_test": test_result.get("generated_test", ""),
            "test_framework": test_result.get("test_framework", "pytest"),
            "processing_time_ms": total_time_ms,
        }
    
    def _store_analysis(
        self,
        result: Dict[str, Any],
        project_id: str,
        user_id: str,
        db: Session
    ) -> AnalysisHistory:
        """Store analysis results in database"""
        analysis = AnalysisHistory(
            project_id=project_id,
            user_id=user_id,
            bug_description=result["bug_description"],
            bug_summary=result.get("bug_summary"),
            bug_type=result.get("bug_type"),
            severity=result.get("severity"),
            affected_files=result["relevant_files"],
            root_cause=result["root_cause"],
            explanation_simple=result["explanation_simple"],
            explanation_technical=result["explanation_technical"],
            suggested_fix=result["suggested_fix"],
            generated_test=result["generated_test"],
            test_framework=result.get("test_framework"),
            processing_time_ms=result["processing_time_ms"]
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return analysis
    
    def _reset_workflow(self):
        """Reset workflow state for new execution"""
        for step in self.workflow_steps.values():
            step.status = "pending"
            step.result = None
            step.error = None
            step.start_time = None
            step.end_time = None
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "steps": [step.to_dict() for step in self.workflow_steps.values()],
            "overall_status": self._get_overall_status()
        }
    
    def _get_overall_status(self) -> str:
        """Determine overall workflow status"""
        statuses = [step.status for step in self.workflow_steps.values()]
        
        if any(s == "failed" for s in statuses):
            return "failed"
        elif any(s == "running" for s in statuses):
            return "running"
        elif all(s == "completed" for s in statuses):
            return "completed"
        else:
            return "pending"

# Made with Bob