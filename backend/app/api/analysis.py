"""Bug analysis API routes"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
import logging
import json
import asyncio
import threading
import queue

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisList, AnalysisListItem
from app.services.project_service import ProjectService
from app.services.analysis_service import AnalysisOrchestrationService
from app.services.vector_service import VectorIndexService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_bug(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a bug using AI agents
    
    This endpoint runs the complete bug analysis pipeline:
    1. Bug Understanding - Extract intent and structure
    2. Code Retrieval - Find relevant code using vector search
    3. Root Cause Analysis - Identify the bug's root cause
    4. Fix Generation - Generate code fix
    5. Test Generation - Generate regression test
    
    Args:
        request: Analysis request with bug description and project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Complete analysis results
        
    Raises:
        HTTPException: If project not found or not indexed
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(
        db,
        request.project_id,
        current_user.id
    )
    
    # Check if project has vector index; auto-build if chunks exist but index file is missing
    vector_service = VectorIndexService()
    if not vector_service.index_exists(str(request.project_id)):
        # Try to rebuild from existing chunks (handles projects parsed before auto-indexing)
        from app.models.code_chunk import CodeChunk
        chunk_count = db.query(CodeChunk).filter(
            CodeChunk.project_id == str(request.project_id)
        ).count()
        if chunk_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project must be parsed before analysis. Parse the repository first."
            )
        logger.info(f"Vector index missing for project {request.project_id}, rebuilding from {chunk_count} chunks")
        try:
            vector_service.create_index(str(request.project_id), db)
        except Exception as idx_err:
            logger.error(f"Auto-index rebuild failed: {idx_err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to build vector index. Please re-parse the repository."
            )
    
    try:
        # Run analysis
        analysis_service = AnalysisOrchestrationService()
        result = analysis_service.analyze_bug(
            request.bug_description,
            str(request.project_id),
            str(current_user.id),
            db
        )

        # Build response — exclude workflow metadata and avoid duplicate keys
        response_data = {k: v for k, v in result.items() if k != "workflow"}
        return AnalysisResponse(
            project_id=request.project_id,
            **response_data
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze/stream")
async def analyze_bug_stream(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a bug with SSE streaming — emits progress events for each agent step,
    then a final 'result' event with the full analysis JSON.
    """
    project = ProjectService.verify_project_ownership(db, request.project_id, current_user.id)

    # Auto-rebuild vector index if missing
    vector_service = VectorIndexService()
    if not vector_service.index_exists(str(request.project_id)):
        from app.models.code_chunk import CodeChunk
        chunk_count = db.query(CodeChunk).filter(
            CodeChunk.project_id == str(request.project_id)
        ).count()
        if chunk_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project must be parsed before analysis. Parse the repository first."
            )
        try:
            vector_service.create_index(str(request.project_id), db)
        except Exception as idx_err:
            logger.error(f"Auto-index rebuild failed: {idx_err}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to build vector index. Please re-parse the repository."
            )

    event_queue: queue.Queue = queue.Queue()
    DONE_SENTINEL = object()

    def run_analysis():
        try:
            analysis_service = AnalysisOrchestrationService()

            def on_progress(event: dict):
                event_queue.put(event)

            result = analysis_service.analyze_bug(
                request.bug_description,
                str(request.project_id),
                str(current_user.id),
                db,
                callback=on_progress,
            )
            result.pop("workflow", None)
            event_queue.put({"type": "result", "data": result})
        except Exception as e:
            logger.error(f"Streaming analysis failed: {e}")
            event_queue.put({"type": "error", "message": str(e)})
        finally:
            event_queue.put(DONE_SENTINEL)

    thread = threading.Thread(target=run_analysis, daemon=True)
    thread.start()

    async def event_generator():
        loop = asyncio.get_event_loop()
        while True:
            try:
                event = await loop.run_in_executor(None, lambda: event_queue.get(timeout=120))
            except queue.Empty:
                yield 'data: {"type":"error","message":"Analysis timed out"}\n\n'
                break

            if event is DONE_SENTINEL:
                break

            if "type" not in event:
                event["type"] = "progress"

            yield f"data: {json.dumps(event, default=str)}\n\n"

        yield 'data: {"type":"done"}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{project_id}/history", response_model=AnalysisList)
async def get_analysis_history(
    project_id: UUID,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analysis history for a project
    
    Args:
        project_id: Project UUID
        page: Page number (starts at 1)
        page_size: Items per page
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of analyses
        
    Raises:
        HTTPException: If project not found
    """
    # Verify project ownership
    project = ProjectService.verify_project_ownership(db, project_id, current_user.id)
    
    # Get history
    analysis_service = AnalysisOrchestrationService()
    skip = (page - 1) * page_size
    analyses, total = analysis_service.get_analysis_history(
        str(project_id),
        db,
        skip,
        page_size
    )
    
    return AnalysisList(
        analyses=[AnalysisListItem.from_orm(a) for a in analyses],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific analysis by ID
    
    Args:
        analysis_id: Analysis UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Analysis details
        
    Raises:
        HTTPException: If analysis not found or access denied
    """
    from app.models.analysis import AnalysisHistory
    
    analysis = db.query(AnalysisHistory).filter(
        AnalysisHistory.id == analysis_id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Verify ownership through project
    project = ProjectService.verify_project_ownership(
        db,
        analysis.project_id,
        current_user.id
    )
    
    return AnalysisResponse(
        analysis_id=analysis.id,
        project_id=analysis.project_id,
        bug_description=analysis.bug_description,
        bug_summary=analysis.bug_summary or analysis.bug_description[:100],
        affected_components=[],
        bug_type=analysis.bug_type or "unknown",
        severity=analysis.severity or "medium",
        relevant_files=analysis.affected_files or [],
        code_chunks=[],
        root_cause=analysis.root_cause or "",
        explanation_technical=analysis.explanation_technical or "",
        suggested_fix=analysis.suggested_fix or "",
        explanation_simple=analysis.explanation_simple or "",
        generated_test=analysis.generated_test or "",
        test_framework=analysis.test_framework or "pytest",
        processing_time_ms=analysis.processing_time_ms or 0,
        created_at=analysis.created_at
    )

# Made with Bob