"""
Task service with business logic.
Handles task CRUD operations with filtering, search, and pagination.
"""

from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models.task import Task, TaskStatus, TaskPriority
from app.schemas.task import TaskCreate, TaskUpdate
from app.repositories.task_repository import task_repository
from app.repositories.category_repository import category_repository
from app.core.exceptions import NotFoundError, ValidationError
import uuid


class TaskService:
    """Task service with business logic."""

    async def create_task(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        task_in: TaskCreate
    ) -> Task:
        """
        Create a new task for user.
        """
        # Validate category if provided
        if task_in.category_id:
            category = await category_repository.get_by_user_and_id(
                db,
                user_id,
                task_in.category_id
            )
            if not category:
                raise NotFoundError("Category not found")

        task_data = task_in.model_dump()
        task_data["user_id"] = user_id

        task = await task_repository.create(db, obj_in=task_data)
        await db.commit()
        await db.refresh(task)

        return task

    async def get_user_tasks(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Task], int]:
        """
        Get all tasks for a user with pagination.
        """
        tasks = await task_repository.get_by_user(db, user_id, skip, limit)
        total = await task_repository.count_user_tasks(db, user_id)

        return tasks, total

    async def get_task(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID
    ) -> Task:
        """
        Get task by ID, ensuring user ownership.
        """
        task = await task_repository.get_by_user_and_id(db, user_id, task_id)
        if not task:
            raise NotFoundError("Task not found")

        return task

    async def update_task(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
        task_update: TaskUpdate
    ) -> Task:
        """
        Update task.
        """
        task = await self.get_task(db, user_id, task_id)

        update_data = task_update.model_dump(exclude_unset=True)
        if not update_data:
            return task

        if "category_id" in update_data and update_data["category_id"]:
            category = await category_repository.get_by_user_and_id(
                db,
                user_id,
                update_data["category_id"]
            )
            if not category:
                raise NotFoundError("Category not found")

        updated_task = await task_repository.update(
            db,
            db_obj=task,
            obj_in=update_data
        )
        await db.commit()
        await db.refresh(updated_task)

        return updated_task

    async def delete_task(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        task_id: uuid.UUID
    ) -> bool:
        """
        Delete task.
        """
        await self.get_task(db, user_id, task_id)

        result = await task_repository.delete(db, id=task_id)
        await db.commit()

        return result

    async def get_tasks_with_filters(
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
        Get tasks with advanced filtering.
        """
        if category_id:
            category = await category_repository.get_by_user_and_id(
                db,
                user_id,
                category_id
            )
            if not category:
                raise NotFoundError("Category not found")

        return await task_repository.get_with_filters(
            db,
            user_id,
            status=status,
            priority=priority,
            category_id=category_id,
            search=search,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            skip=skip,
            limit=limit
        )

    async def get_overdue_tasks(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get overdue tasks for user.
        """
        return await task_repository.get_overdue_tasks(db, user_id, skip, limit)

    async def get_task_statistics(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> dict:
        """
        Get task statistics for user.
        """
        total = await task_repository.count_user_tasks(db, user_id)
        todo = await task_repository.count_user_tasks(db, user_id, TaskStatus.TODO)
        in_progress = await task_repository.count_user_tasks(db, user_id, TaskStatus.IN_PROGRESS)
        completed = await task_repository.count_user_tasks(db, user_id, TaskStatus.COMPLETED)
        archived = await task_repository.count_user_tasks(db, user_id, TaskStatus.ARCHIVED)

        overdue_tasks = await task_repository.get_overdue_tasks(db, user_id, 0, 1)
        overdue_count = len(overdue_tasks)

        return {
            "total": total,
            "by_status": {
                "todo": todo,
                "in_progress": in_progress,
                "completed": completed,
                "archived": archived
            },
            "overdue": overdue_count
        }


# Global service instance
task_service = TaskService()
