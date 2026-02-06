"""
Main API router for v1 endpoints.
Aggregates all route modules.
"""

from fastapi import APIRouter
from app.api.v1 import auth, users, tasks, categories

# Create main API router
api_router = APIRouter()

# Include sub-routers with prefixes and tags
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"]
)