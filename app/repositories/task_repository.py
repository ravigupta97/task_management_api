
"""
Task repository for database operations.
Extends BaseRepository with task-specific queries, filtering, and search.
"""

from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from datetime import datetime
from app.models.task import Task, TaskStatus, TaskPriority
from app.repositories.base import BaseRepository
import uuid


class TaskRepository(BaseRepository[Task]):
    """Task-specific repository with advanced querying."""
    
    def __init__(self):
        super().__init__(Task)
    
    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get all tasks for a specific user.
        
        Args:
            db: Database session
            user_id: User's UUID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of user's tasks
        """
        result = await db.execute(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_user_and_id(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID
    ) -> Optional[Task]:
        """
        Get task by ID, ensuring it belongs to the user.
        
        Args:
            db: Database session
            user_id: User's UUID
            task_id: Task's UUID
            
        Returns:
            Task if found and owned by user, None otherwise
        """
        result = await db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_with_filters(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        *,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        category_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Task], int]:
        """
        Get tasks with advanced filtering and search.
        
        Args:
            db: Database session
            user_id: User's UUID
            status: Filter by status
            priority: Filter by priority
            category_id: Filter by category
            search: Search in title and description
            due_date_from: Filter tasks due after this date
            due_date_to: Filter tasks due before this date
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            Tuple of (list of tasks, total count)
        """
        # Base query
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.where(Task.status == status)
        
        if priority:
            query = query.where(Task.priority == priority)
        
        if category_id:
            query = query.where(Task.category_id == category_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term)
                )
            )
        
        if due_date_from:
            query = query.where(Task.due_date >= due_date_from)
        
        if due_date_to:
            query = query.where(Task.due_date <= due_date_to)
        
        # Count total matching records
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination and ordering
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        tasks = list(result.scalars().all())
        
        return tasks, total
    
    async def get_by_status(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: TaskStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks by status for a user.
        
        Args:
            db: Database session
            user_id: User's UUID
            status: Task status
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of tasks with specified status
        """
        result = await db.execute(
            select(Task)
            .where(Task.user_id == user_id, Task.status == status)
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_category(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks by category for a user.
        
        Args:
            db: Database session
            user_id: User's UUID
            category_id: Category's UUID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of tasks in specified category
        """
        result = await db.execute(
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.category_id == category_id
            )
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_overdue_tasks(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get overdue tasks for a user.
        
        Args:
            db: Database session
            user_id: User's UUID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of overdue tasks
        """
        result = await db.execute(
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.status != TaskStatus.COMPLETED,
                Task.due_date < datetime.utcnow()
            )
            .order_by(Task.due_date.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_user_tasks(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[TaskStatus] = None
    ) -> int:
        """
        Count tasks for a user, optionally filtered by status.
        
        Args:
            db: Database session
            user_id: User's UUID
            status: Optional status filter
            
        Returns:
            Number of tasks
        """
        query = select(func.count(Task.id)).where(Task.user_id == user_id)
        
        if status:
            query = query.where(Task.status == status)
        
        result = await db.execute(query)
        return result.scalar_one()
    
    async def count_by_category(
        self,
        db: AsyncSession,
        category_id: uuid.UUID
    ) -> int:
        """
        Count tasks in a category.
        
        Args:
            db: Database session
            category_id: Category's UUID
            
        Returns:
            Number of tasks in category
        """
        result = await db.execute(
            select(func.count(Task.id)).where(Task.category_id == category_id)
        )
        return result.scalar_one()


# Global repository instance
task_repository = TaskRepository()