"""
Pydantic schemas package.
Centralized exports for all schemas.
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
    UserResponse,
    UserLogin,
    UserInDB,
    PasswordResetRequest,
    PasswordReset,
    EmailVerificationRequest,
    ResendVerificationRequest
)

from app.schemas.token import (
    Token,
    TokenPayload,
    RefreshTokenRequest,
    RefreshTokenResponse
)

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryInDB,
    CategoryWithTasks
)

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskInDB,
    TaskWithCategory,
    TaskListResponse,
    PaginationParams,
    TaskFilterParams
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserUpdatePassword",
    "UserResponse",
    "UserLogin",
    "UserInDB",
    "PasswordResetRequest",
    "PasswordReset",
    "EmailVerificationRequest",
    "ResendVerificationRequest",
    
    # Token schemas
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    
    # Category schemas
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryInDB",
    "CategoryWithTasks",
    
    # Task schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskInDB",
    "TaskWithCategory",
    "TaskListResponse",
    "PaginationParams",
    "TaskFilterParams",
]