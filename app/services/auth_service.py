
"""
Authentication service with business logic for user authentication.
Handles registration, login, token refresh, password reset, email verification.
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, PasswordReset
from app.schemas.token import Token, RefreshTokenResponse
from app.repositories.user_repository import user_repository
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    create_verification_token,
    verify_token,
    REFRESH_TOKEN_TYPE,
    RESET_TOKEN_TYPE,
    VERIFICATION_TOKEN_TYPE
)
from app.core.exceptions import (
    AuthenticationError,
    AlreadyExistsError,
    NotFoundError,
    InvalidTokenError,
    InactiveUserError,
    UnverifiedUserError
)
import uuid


class AuthService:
    """Authentication service with business logic."""
    
    async def register(self, db: AsyncSession, user_in: UserCreate) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_in: User registration data
            
        Returns:
            Dictionary with user and verification token
            
        Raises:
            AlreadyExistsError: If email or username already exists
        """
        # Check if email exists
        if await user_repository.email_exists(db, user_in.email):
            raise AlreadyExistsError("Email already registered")
        
        # Check if username exists
        if await user_repository.username_exists(db, user_in.username):
            raise AlreadyExistsError("Username already taken")
        
        # Create user with hashed password
        user_dict = user_in.model_dump(exclude={"password"})
        user_dict["hashed_password"] = get_password_hash(user_in.password)
        user_dict["is_active"] = True
        user_dict["is_verified"] = False  # Requires email verification
        
        user = await user_repository.create(db, obj_in=user_dict)
        await db.commit()
        
        # Generate verification token
        verification_token = create_verification_token(user.email)
        
        return {
            "user": user,
            "verification_token": verification_token
        }
    
    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> User:
        """
        Authenticate user with username/email and password.
        
        Args:
            db: Database session
            username: Username or email
            password: Plain password
            
        Returns:
            Authenticated user
            
        Raises:
            AuthenticationError: If credentials are invalid
            InactiveUserError: If user account is inactive
        """
        # Find user by username or email
        user = await user_repository.get_by_email_or_username(db, username)
        
        if not user:
            raise AuthenticationError("Incorrect username or password")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Incorrect username or password")
        
        # Check if user is active
        if not user.is_active:
            raise InactiveUserError()
        
        return user
    
    async def login(
        self,
        db: AsyncSession,
        username: str,
        password: str
    ) -> Token:
        """
        Login user and return tokens.
        
        Args:
            db: Database session
            username: Username or email
            password: Plain password
            
        Returns:
            Token response with access and refresh tokens
        """
        # Authenticate user
        user = await self.authenticate(db, username, password)
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str
    ) -> RefreshTokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            InvalidTokenError: If refresh token is invalid
            NotFoundError: If user not found
        """
        # Verify refresh token
        user_id_str = verify_token(refresh_token, REFRESH_TOKEN_TYPE)
        
        if not user_id_str:
            raise InvalidTokenError("Invalid refresh token")
        
        # Get user
        user = await user_repository.get(db, uuid.UUID(user_id_str))
        
        if not user:
            raise NotFoundError("User not found")
        
        if not user.is_active:
            raise InactiveUserError()
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer"
        )
    
    async def request_password_reset(
        self,
        db: AsyncSession,
        email: str
    ) -> str:
        """
        Generate password reset token.
        
        Args:
            db: Database session
            email: User's email
            
        Returns:
            Password reset token
            
        Note:
            Always returns successfully even if email doesn't exist
            (security best practice - don't reveal if email is registered)
        """
        # Check if user exists (but don't reveal if they don't)
        user = await user_repository.get_by_email(db, email)
        
        if not user:
            # Still return a token to prevent email enumeration
            # This token will be invalid when trying to reset
            return create_reset_token(email)
        
        # Generate reset token
        reset_token = create_reset_token(email)
        
        return reset_token
    
    async def reset_password(
        self,
        db: AsyncSession,
        reset_data: PasswordReset
    ) -> bool:
        """
        Reset password using reset token.
        
        Args:
            db: Database session
            reset_data: Password reset data with token and new password
            
        Returns:
            True if successful
            
        Raises:
            InvalidTokenError: If reset token is invalid
            NotFoundError: If user not found
        """
        # Verify reset token
        email = verify_token(reset_data.token, RESET_TOKEN_TYPE)
        
        if not email:
            raise InvalidTokenError("Invalid or expired reset token")
        
        # Get user
        user = await user_repository.get_by_email(db, email)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Update password
        hashed_password = get_password_hash(reset_data.new_password)
        await user_repository.update(
            db,
            db_obj=user,
            obj_in={"hashed_password": hashed_password}
        )
        await db.commit()
        
        return True
    
    async def verify_email(
        self,
        db: AsyncSession,
        token: str
    ) -> bool:
        """
        Verify user's email using verification token.
        
        Args:
            db: Database session
            token: Email verification token
            
        Returns:
            True if successful
            
        Raises:
            InvalidTokenError: If verification token is invalid
            NotFoundError: If user not found
        """
        # Verify token
        email = verify_token(token, VERIFICATION_TOKEN_TYPE)
        
        if not email:
            raise InvalidTokenError("Invalid or expired verification token")
        
        # Get user
        user = await user_repository.get_by_email(db, email)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Mark as verified
        await user_repository.update(
            db,
            db_obj=user,
            obj_in={"is_verified": True}
        )
        await db.commit()
        
        return True
    
    async def resend_verification(
        self,
        db: AsyncSession,
        email: str
    ) -> str:
        """
        Resend email verification token.
        
        Args:
            db: Database session
            email: User's email
            
        Returns:
            New verification token
            
        Raises:
            NotFoundError: If user not found
        """
        # Get user
        user = await user_repository.get_by_email(db, email)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Generate new verification token
        verification_token = create_verification_token(email)
        
        return verification_token


# Global service instance
auth_service = AuthService()