
"""
Main API router for v1 endpoints.
Aggregates all route modules.
"""

from fastapi import APIRouter
from app.api.v1 import auth, users

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

