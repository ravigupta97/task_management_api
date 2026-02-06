
"""
Category service with business logic.
Handles category CRUD operations with user ownership validation.
"""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories.category_repository import category_repository
from app.repositories.task_repository import task_repository
from app.core.exceptions import AlreadyExistsError, NotFoundError
import uuid


class CategoryService:
    """Category service with business logic."""
    
    async def create_category(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category_in: CategoryCreate
    ) -> Category:
        """
        Create a new category for user.
        
        Args:
            db: Database session
            user_id: Owner's UUID
            category_in: Category creation data
            
        Returns:
            Created category
            
        Raises:
            AlreadyExistsError: If category name already exists for user
        """
        # Check if category name already exists for this user
        if await category_repository.name_exists_for_user(
            db,
            user_id,
            category_in.name
        ):
            raise AlreadyExistsError(
                f"Category '{category_in.name}' already exists"
            )
        
        # Create category
        category_data = category_in.model_dump()
        category_data["user_id"] = user_id
        
        category = await category_repository.create(db, obj_in=category_data)
        await db.commit()
        await db.refresh(category)
        
        return category
    
    async def get_user_categories(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Category]:
        """
        Get all categories for a user.
        
        Args:
            db: Database session
            user_id: User's UUID
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of categories
        """
        return await category_repository.get_by_user(db, user_id, skip, limit)
    
    async def get_category(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category_id: uuid.UUID
    ) -> Category:
        """
        Get category by ID, ensuring user ownership.
        
        Args:
            db: Database session
            user_id: User's UUID
            category_id: Category's UUID
            
        Returns:
            Category instance
            
        Raises:
            NotFoundError: If category not found or not owned by user
        """
        category = await category_repository.get_by_user_and_id(
            db,
            user_id,
            category_id
        )
        
        if not category:
            raise NotFoundError("Category not found")
        
        return category
    
    async def update_category(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category_id: uuid.UUID,
        category_update: CategoryUpdate
    ) -> Category:
        """
        Update category.
        
        Args:
            db: Database session
            user_id: User's UUID
            category_id: Category's UUID
            category_update: Update data
            
        Returns:
            Updated category
            
        Raises:
            NotFoundError: If category not found
            AlreadyExistsError: If new name already exists
        """
        # Get existing category
        category = await self.get_category(db, user_id, category_id)
        
        # Get update data
        update_data = category_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return category
        
        # Check if new name conflicts
        if "name" in update_data:
            if await category_repository.name_exists_for_user(
                db,
                user_id,
                update_data["name"],
                exclude_id=category_id
            ):
                raise AlreadyExistsError(
                    f"Category '{update_data['name']}' already exists"
                )
        
        # Update category
        updated_category = await category_repository.update(
            db,
            db_obj=category,
            obj_in=update_data
        )
        await db.commit()
        await db.refresh(updated_category)
        
        return updated_category
    
    async def delete_category(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category_id: uuid.UUID
    ) -> bool:
        """
        Delete category.
        
        Note: Tasks in this category will have their category_id set to NULL
        (due to ondelete="SET NULL" in the foreign key)
        
        Args:
            db: Database session
            user_id: User's UUID
            category_id: Category's UUID
            
        Returns:
            True if deleted
            
        Raises:
            NotFoundError: If category not found
        """
        # Verify ownership
        await self.get_category(db, user_id, category_id)
        
        # Delete category
        result = await category_repository.delete(db, id=category_id)
        await db.commit()
        
        return result
    
    async def get_category_with_task_count(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        category_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Get category with task count.
        
        Args:
            db: Database session
            user_id: User's UUID
            category_id: Category's UUID
            
        Returns:
            Dictionary with category and task_count
        """
        category = await self.get_category(db, user_id, category_id)
        task_count = await task_repository.count_by_category(db, category_id)
        
        return {
            "category": category,
            "task_count": task_count
        }


# Global service instance
category_service = CategoryService()