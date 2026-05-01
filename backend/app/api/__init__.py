"""API routes"""

from fastapi import APIRouter
from app.api import auth, projects, repository, parsing

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(repository.router, prefix="/repository", tags=["Repository"])
api_router.include_router(parsing.router, prefix="/parsing", tags=["Code Parsing"])

__all__ = ["api_router"]

# Made with Bob
