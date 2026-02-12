"""
Main API router for v1 endpoints.
Aggregates all route modules with enhanced documentation.
"""

from fastapi import APIRouter
from app.api.v1 import auth, users, tasks, categories

# Create main API router
api_router = APIRouter()

# Define tag metadata for better documentation
tags_metadata = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization operations. "
                      "Includes registration, login, token refresh, password reset, and email verification."
    },
    {
        "name": "Users",
        "description": "User profile management operations. "
                      "Allows users to view, update, and delete their profiles."
    },
    {
        "name": "Tasks",
        "description": "Task management operations. "
                      "Create, read, update, and delete tasks with advanced filtering, search, and pagination."
    },
    {
        "name": "Categories",
        "description": "Category management operations. "
                      "Organize tasks into custom categories with color coding."
    },
]

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