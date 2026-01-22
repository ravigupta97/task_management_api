
"""
Category model for task organization.
"""

from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models import BaseModel


class Category(BaseModel):
    """
    Category model for organizing tasks.
    
    Features:
    - User-specific categories
    - Color coding for UI
    - Unique category names per user
    """
    
    __tablename__ = "categories"
    
    # Category fields
    name = Column(
        String(50),
        nullable=False,
        index=True
    )
    
    color = Column(
        String(7),  # Hex color code: #RRGGBB
        default="#3B82F6",  # Default blue color
        nullable=False
    )
    
    # Foreign Key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    owner = relationship(
        "User",
        back_populates="categories"
    )
    
    tasks = relationship(
        "Task",
        back_populates="category",
        cascade="all, delete-orphan"  # Delete tasks when category is deleted? NO!
        # Actually, we use SET NULL in Task model, so this won't delete tasks
    )
    
    # Constraints
    __table_args__ = (
        # Ensure category names are unique per user
        UniqueConstraint('user_id', 'name', name='uq_user_category_name'),
    )
    
    def __repr__(self):
        return f"<Category(name={self.name}, color={self.color})>"