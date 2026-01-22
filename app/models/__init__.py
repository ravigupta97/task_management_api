"""
Database models package.
Exports Base and all model classes for easy imports.
"""

from app.database import Base
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class BaseModel(Base):
    """
    Abstract base model with common fields for all tables.
    
    Provides:
    - UUID primary key (more secure than auto-increment integers)
    - Created timestamp (automatically set)
    - Updated timestamp (automatically updated)
    """
    
    __abstract__ = True  # Don't create a table for this class
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    def __repr__(self):
        """String representation for debugging."""
        return f"<{self.__class__.__name__}(id={self.id})>"


# Import models here for easy access
# This allows: from app.models import User, Task, Category
from app.models.user import User  # noqa: E402
from app.models.task import Task, TaskStatus, TaskPriority  # noqa: E402
from app.models.category import Category  # noqa: E402

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "Category"
]