"""
Task model with status and priority enums.
"""

from sqlalchemy import Column, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
from app.models import BaseModel


class TaskStatus(str, enum.Enum):
    """
    Task status enumeration.
    Using str enum for better JSON serialization.
    """
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class TaskPriority(str, enum.Enum):
    """
    Task priority enumeration.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Task(BaseModel):
    """
    Task model with rich metadata and relationships.
    
    Relationships:
    - Many-to-One with User (many tasks belong to one user)
    - Many-to-One with Category (many tasks belong to one category)
    """
    
    __tablename__ = "tasks"
    
    # Core task fields
    title = Column(
        String(200),
        nullable=False,
        index=True  # Index for search performance
    )
    
    description = Column(
        Text,
        nullable=True
    )
    
    # Status and priority
    status = Column(
        Enum(TaskStatus),
        default=TaskStatus.TODO,
        nullable=False,
        index=True  # Index for filtering by status
    )
    
    priority = Column(
        Enum(TaskPriority),
        default=TaskPriority.MEDIUM,
        nullable=False,
        index=True  # Index for filtering by priority
    )
    
    # Optional due date
    due_date = Column(
        DateTime,
        nullable=True,
        index=True  # Index for date range queries
    )
    
    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Relationships
    owner = relationship(
        "User",
        back_populates="tasks"
    )
    
    category = relationship(
        "Category",
        back_populates="tasks"
    )
    
    def __repr__(self):
        return f"<Task(title={self.title}, status={self.status}, priority={self.priority})>"
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.utcnow() > self.due_date
        return False
