
"""
User model for authentication and user management.
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models import BaseModel


class User(BaseModel):
    """
    User model with authentication fields.
    
    Relationships:
    - One-to-Many with Task (one user has many tasks)
    - One-to-Many with Category (one user has many categories)
    """
    
    __tablename__ = "users"
    
    # Authentication fields
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    
    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    
    hashed_password = Column(
        String(255),
        nullable=False
    )
    
    # Account status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Additional profile fields (optional - can be extended)
    full_name = Column(String(100), nullable=True)
    
    # Relationships
    tasks = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",  # Delete tasks when user is deleted
        lazy="selectin"  # Eager loading strategy
    )
    
    categories = relationship(
        "Category",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"