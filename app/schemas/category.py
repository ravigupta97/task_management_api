
"""
Pydantic schemas for Category model.
Request/response validation for category-related endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class CategoryBase(BaseModel):
    """Base category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(
        default="#3B82F6",
        pattern="^#[0-9A-Fa-f]{6}$",  # Hex color validation
        description="Hex color code (e.g., #FF5733)"
    )


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(
        None,
        pattern="^#[0-9A-Fa-f]{6}$"
    )


class CategoryInDB(CategoryBase):
    """Schema for category as stored in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(CategoryInDB):
    """Schema for category in API responses."""
    task_count: Optional[int] = None  # Optional: number of tasks in category

from app.schemas.task import TaskResponse
from typing import List

class CategoryWithTasks(CategoryInDB):
    """Schema for category with associated tasks."""
    
    tasks: List["TaskResponse"] = []