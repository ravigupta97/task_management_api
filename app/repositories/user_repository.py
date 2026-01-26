
"""
User repository for database operations.
Extends BaseRepository with user-specific queries.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User-specific repository."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User's email
            
        Returns:
            User instance or None
        """
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User instance or None
        """
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email_or_username(
        self,
        db: AsyncSession,
        identifier: str
    ) -> Optional[User]:
        """
        Get user by email OR username (for login).
        
        Args:
            db: Database session
            identifier: Email or username
            
        Returns:
            User instance or None
        """
        result = await db.execute(
            select(User).where(
                or_(User.email == identifier, User.username == identifier)
            )
        )
        return result.scalar_one_or_none()
    
    async def email_exists(self, db: AsyncSession, email: str) -> bool:
        """
        Check if email already exists.
        
        Args:
            db: Database session
            email: Email to check
            
        Returns:
            True if exists, False otherwise
        """
        result = await db.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None
    
    async def username_exists(self, db: AsyncSession, username: str) -> bool:
        """
        Check if username already exists.
        
        Args:
            db: Database session
            username: Username to check
            
        Returns:
            True if exists, False otherwise
        """
        result = await db.execute(
            select(User.id).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None


# Global repository instance
user_repository = UserRepository()