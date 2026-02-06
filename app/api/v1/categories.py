
"""
Category API endpoints.
Handles category CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.deps import get_db, get_current_active_user
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithTasks
)
from app.services.category_service import category_service
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.user import User
import uuid

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new category.
    
    - **name**: Category name (unique per user, 1-50 characters)
    - **color**: Hex color code (e.g., #FF5733)
    
    The category will be owned by the authenticated user.
    """
    try:
        category = await category_service.create_category(
            db,
            user_id=current_user.id,
            category_in=category_in
        )
        return CategoryResponse.model_validate(category)
        
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/", response_model=List[CategoryResponse])
async def get_my_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all categories for the authenticated user.
    
    Supports pagination with skip and limit parameters.
    """
    categories = await category_service.get_user_categories(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return [CategoryResponse.model_validate(cat) for cat in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific category by ID.
    
    Returns 404 if category not found or doesn't belong to user.
    """
    try:
        category = await category_service.get_category(
            db,
            user_id=current_user.id,
            category_id=category_id
        )
        return CategoryResponse.model_validate(category)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a category.
    
    - **name**: New category name (optional)
    - **color**: New color code (optional)
    
    All fields are optional. Only provided fields will be updated.
    """
    try:
        category = await category_service.update_category(
            db,
            user_id=current_user.id,
            category_id=category_id,
            category_update=category_update
        )
        return CategoryResponse.model_validate(category)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a category.
    
    Tasks in this category will have their category_id set to NULL.
    This action is irreversible.
    """
    try:
        await category_service.delete_category(
            db,
            user_id=current_user.id,
            category_id=category_id
        )
        return None
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{category_id}/stats", response_model=dict)
async def get_category_stats(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get category statistics including task count.
    """
    try:
        stats = await category_service.get_category_with_task_count(
            db,
            user_id=current_user.id,
            category_id=category_id
        )
        
        category_data = CategoryResponse.model_validate(stats["category"])
        
        return {
            "category": category_data,
            "task_count": stats["task_count"]
        }
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )