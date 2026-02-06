
"""
Pydantic schemas for Task model.
Request/response validation for task-related endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    category_id: Optional[uuid.UUID] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    category_id: Optional[uuid.UUID] = None


class TaskInDB(TaskBase):
    """Schema for task as stored in database."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskInDB):
    """Schema for task in API responses."""
    is_overdue: bool = False
    
    @classmethod
    def from_orm_with_overdue(cls, task):
        """Create response with is_overdue calculated."""
        data = cls.model_validate(task)
        data.is_overdue = task.is_overdue
        return data

from app.schemas.category import CategoryResponse

class TaskWithCategory(TaskInDB):
    """Schema for task with category details."""
    
    
    category: Optional["CategoryResponse"] = None


class TaskListResponse(BaseModel):
    """Schema for paginated task list."""
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Pagination schema
class PaginationParams(BaseModel):
    """Common pagination parameters."""
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of items to return")


# Filter schema
class TaskFilterParams(BaseModel):
    """Task filtering parameters."""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[uuid.UUID] = None
    search: Optional[str] = Field(None, max_length=200)
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None