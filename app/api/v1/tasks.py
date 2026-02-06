
"""
Task API endpoints.
Handles task CRUD operations with filtering, pagination, and search.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.api.deps import get_db, get_current_active_user
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse
)
from app.models.task import TaskStatus, TaskPriority
from app.services.task_service import task_service
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
import uuid
import math

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task.
    
    - **title**: Task title (required, 1-200 characters)
    - **description**: Task description (optional)
    - **status**: Task status (default: TODO)
    - **priority**: Task priority (default: MEDIUM)
    - **due_date**: Due date (optional, ISO 8601 format)
    - **category_id**: Category UUID (optional)
    
    The task will be owned by the authenticated user.
    """
    try:
        task = await task_service.create_task(
            db,
            user_id=current_user.id,
            task_in=task_in
        )
        
        response = TaskResponse.model_validate(task)
        response.is_overdue = task.is_overdue
        return response
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/", response_model=TaskListResponse)
async def get_my_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records"),
    status_filter: Optional[TaskStatus] = Query(None, alias="status", description="Filter by status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority", description="Filter by priority"),
    category_id: Optional[uuid.UUID] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, max_length=200, description="Search in title and description"),
    due_date_from: Optional[datetime] = Query(None, description="Filter by due date (from)"),
    due_date_to: Optional[datetime] = Query(None, description="Filter by due date (to)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get tasks with filtering, search, and pagination.
    
    **Filtering:**
    - status: Filter by task status (TODO, IN_PROGRESS, COMPLETED, ARCHIVED)
    - priority: Filter by priority (LOW, MEDIUM, HIGH, URGENT)
    - category_id: Filter by category UUID
    - due_date_from: Tasks due after this date
    - due_date_to: Tasks due before this date
    
    **Search:**
    - search: Search term for title and description (case-insensitive)
    
    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 10, max: 100)
    """
    try:
        tasks, total = await task_service.get_tasks_with_filters(
            db,
            user_id=current_user.id,
            status=status_filter,
            priority=priority_filter,
            category_id=category_id,
            search=search,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            skip=skip,
            limit=limit
        )
        
        # Calculate pagination info
        page = (skip // limit) + 1
        total_pages = math.ceil(total / limit) if total > 0 else 0
        
        # Convert tasks to response models
        task_responses = []
        for task in tasks:
            task_response = TaskResponse.model_validate(task)
            task_response.is_overdue = task.is_overdue
            task_responses.append(task_response)
        
        return TaskListResponse(
            items=task_responses,
            total=total,
            page=page,
            page_size=limit,
            total_pages=total_pages
        )
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all overdue tasks for the authenticated user.
    
    Returns tasks that:
    - Have a due_date in the past
    - Are not completed
    
    Sorted by due_date (oldest first).
    """
    tasks = await task_service.get_overdue_tasks(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    task_responses = []
    for task in tasks:
        task_response = TaskResponse.model_validate(task)
        task_response.is_overdue = task.is_overdue
        task_responses.append(task_response)
    
    return task_responses


@router.get("/statistics", response_model=dict)
async def get_task_statistics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get task statistics for the authenticated user.
    
    Returns:
    - Total task count
    - Count by status (TODO, IN_PROGRESS, COMPLETED, ARCHIVED)
    - Overdue task count
    """
    stats = await task_service.get_task_statistics(
        db,
        user_id=current_user.id
    )
    return stats


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific task by ID.
    
    Returns 404 if task not found or doesn't belong to user.
    """
    try:
        task = await task_service.get_task(
            db,
            user_id=current_user.id,
            task_id=task_id
        )
        
        response = TaskResponse.model_validate(task)
        response.is_overdue = task.is_overdue
        return response
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a task.
    
    All fields are optional. Only provided fields will be updated.
    
    - **title**: New task title
    - **description**: New description
    - **status**: New status
    - **priority**: New priority
    - **due_date**: New due date
    - **category_id**: New category (use null to remove category)
    """
    try:
        task = await task_service.update_task(
            db,
            user_id=current_user.id,
            task_id=task_id,
            task_update=task_update
        )
        
        response = TaskResponse.model_validate(task)
        response.is_overdue = task.is_overdue
        return response
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a task.
    
    This action is irreversible.
    """
    try:
        await task_service.delete_task(
            db,
            user_id=current_user.id,
            task_id=task_id
        )
        return None
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    task_id: uuid.UUID,
    new_status: TaskStatus,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick update for task status only.
    
    Convenience endpoint for changing task status without sending full update.
    """
    try:
        task_update = TaskUpdate(status=new_status)
        task = await task_service.update_task(
            db,
            user_id=current_user.id,
            task_id=task_id,
            task_update=task_update
        )
        
        response = TaskResponse.model_validate(task)
        response.is_overdue = task.is_overdue
        return response
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{task_id}/priority", response_model=TaskResponse)
async def update_task_priority(
    task_id: uuid.UUID,
    new_priority: TaskPriority,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick update for task priority only.
    
    Convenience endpoint for changing task priority without sending full update.
    """
    try:
        task_update = TaskUpdate(priority=new_priority)
        task = await task_service.update_task(
            db,
            user_id=current_user.id,
            task_id=task_id,
            task_update=task_update
        )
        
        response = TaskResponse.model_validate(task)
        response.is_overdue = task.is_overdue
        return response
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )