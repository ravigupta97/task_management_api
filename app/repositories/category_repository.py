
"""
Category repository for database operations.
Extends BaseRepository with category-specific queries.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.category import Category
from app.repositories.base import BaseRepository
import uuid


class CategoryRepository(BaseRepository[Category]):
    """Category-specific repository."""
    
    def __init__(self):
        super().__init__(Category)
    
    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """
        Get all categories for a specific user.
        
        Args:
            db: Database session
            user_id: User's UUID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of user's categories
        """
        result = await db.execute(
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_user_and_id(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category_id: uuid.UUID
    ) -> Optional[Category]:
        """
        Get category by ID, ensuring it belongs to the user.
        
        Args:
            db: Database session
            user_id: User's UUID
            category_id: Category's UUID
            
        Returns:
            Category if found and owned by user, None otherwise
        """
        result = await db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str
    ) -> Optional[Category]:
        """
        Get category by name for a specific user.
        
        Args:
            db: Database session
            user_id: User's UUID
            name: Category name
            
        Returns:
            Category if found, None otherwise
        """
        result = await db.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.name == name
            )
        )
        return result.scalar_one_or_none()
    
    async def name_exists_for_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if category name exists for user.
        
        Args:
            db: Database session
            user_id: User's UUID
            name: Category name to check
            exclude_id: Category ID to exclude (for updates)
            
        Returns:
            True if name exists, False otherwise
        """
        query = select(Category.id).where(
            Category.user_id == user_id,
            Category.name == name
        )
        
        if exclude_id:
            query = query.where(Category.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_user_categories(
        self,
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> int:
        """
        Count total categories for a user.
        
        Args:
            db: Database session
            user_id: User's UUID
            
        Returns:
            Number of categories
        """
        result = await db.execute(
            select(func.count(Category.id)).where(Category.user_id == user_id)
        )
        return result.scalar_one()


# Global repository instance
category_repository = CategoryRepository()