"""API routes"""

from fastapi import APIRouter
from app.api import auth, projects

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

__all__ = ["api_router"]

# Made with Bob
