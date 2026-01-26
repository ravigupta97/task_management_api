
"""
User management API endpoints.
Handles user profile operations (get, update, delete).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_active_user, get_current_verified_user
from app.schemas.user import UserResponse, UserUpdate, UserUpdatePassword
from app.repositories.user_repository import user_repository
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import AlreadyExistsError, AuthenticationError
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile.
    
    Requires authentication.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.
    
    - **email**: New email (must be unique)
    - **username**: New username (must be unique)
    - **full_name**: New full name
    
    All fields are optional.
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    if not update_data:
        return UserResponse.model_validate(current_user)
    
    # Check email uniqueness
    if "email" in update_data:
        existing_user = await user_repository.get_by_email(db, update_data["email"])
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        # If email changes, mark as unverified
        update_data["is_verified"] = False
    
    # Check username uniqueness
    if "username" in update_data:
        existing_user = await user_repository.get_by_username(db, update_data["username"])
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
    
    # Update user
    updated_user = await user_repository.update(
        db,
        db_obj=current_user,
        obj_in=update_data
    )
    await db.commit()
    
    return UserResponse.model_validate(updated_user)


@router.put("/me/password", response_model=dict)
async def update_my_password(
    password_update: UserUpdatePassword,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 8 characters)
    """
    # Verify current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    hashed_password = get_password_hash(password_update.new_password)
    await user_repository.update(
        db,
        db_obj=current_user,
        obj_in={"hashed_password": hashed_password}
    )
    await db.commit()
    
    return {"message": "Password updated successfully"}


@router.delete("/me", response_model=dict)
async def delete_my_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user's account.
    
    This action is irreversible. All user data will be permanently deleted.
    """
    await user_repository.delete(db, id=current_user.id)
    await db.commit()
    
    return {"message": "Account deleted successfully"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (public profile).
    
    Requires authentication to prevent scraping.
    """
    import uuid
    
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    user = await user_repository.get(db, user_uuid)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)