
"""
Authentication API endpoints.
Handles user registration, login, token refresh, password reset, email verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_active_user
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    PasswordResetRequest,
    PasswordReset,
    EmailVerificationRequest,
    ResendVerificationRequest
)
from app.schemas.token import Token, RefreshTokenRequest, RefreshTokenResponse
from app.services.auth_service import auth_service
from app.core.exceptions import (
    AuthenticationError,
    AlreadyExistsError,
    InvalidTokenError,
    NotFoundError,
    InactiveUserError
)
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Valid email address (unique)
    - **username**: Username (unique, 3-50 characters)
    - **password**: Password (minimum 8 characters)
    - **full_name**: Optional full name
    
    Returns user data and verification token.
    In production, verification token should be sent via email.
    """
    try:
        result = await auth_service.register(db, user_in)
        
        # TODO: Send verification email in background
        # background_tasks.add_task(
        #     send_verification_email,
        #     email=result["user"].email,
        #     token=result["verification_token"]
        # )
        
        return {
            "message": "User registered successfully. Please verify your email.",
            "user": UserResponse.model_validate(result["user"]),
            "verification_token": result["verification_token"]  # Remove in production
        }
        
    except AlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username/email and password.
    
    - **username**: Username or email address
    - **password**: User's password
    
    Returns access token and refresh token.
    """
    try:
        token = await auth_service.login(
            db,
            username=login_data.username,
            password=login_data.password
        )
        return token
        
    except (AuthenticationError, InactiveUserError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token.
    """
    try:
        token_response = await auth_service.refresh_token(
            db,
            refresh_token=refresh_data.refresh_token
        )
        return token_response
        
    except (InvalidTokenError, NotFoundError, InactiveUserError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/password-reset/request", response_model=dict)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset token.
    
    - **email**: User's email address
    
    Always returns success (security best practice).
    Reset token should be sent via email in production.
    """
    reset_token = await auth_service.request_password_reset(db, reset_request.email)
    
    # TODO: Send reset email in background
    # background_tasks.add_task(
    #     send_password_reset_email,
    #     email=reset_request.email,
    #     token=reset_token
    # )
    
    return {
        "message": "If the email exists, a password reset link has been sent.",
        "reset_token": reset_token  # Remove in production
    }


@router.post("/password-reset/confirm", response_model=dict)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using reset token.
    
    - **token**: Password reset token
    - **new_password**: New password (minimum 8 characters)
    
    Returns success message.
    """
    try:
        await auth_service.reset_password(db, reset_data)
        return {"message": "Password reset successfully"}
        
    except (InvalidTokenError, NotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-email", response_model=dict)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email using verification token.
    
    - **token**: Email verification token
    
    Returns success message.
    """
    try:
        await auth_service.verify_email(db, verification_data.token)
        return {"message": "Email verified successfully"}
        
    except (InvalidTokenError, NotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/resend-verification", response_model=dict)
async def resend_verification(
    resend_request: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Resend email verification token.
    
    - **email**: User's email address
    
    Returns new verification token.
    """
    try:
        verification_token = await auth_service.resend_verification(
            db,
            resend_request.email
        )
        
        # TODO: Send verification email in background
        # background_tasks.add_task(
        #     send_verification_email,
        #     email=resend_request.email,
        #     token=verification_token
        # )
        
        return {
            "message": "Verification email sent",
            "verification_token": verification_token  # Remove in production
        }
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    
    Requires valid access token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user.
    
    Note: With JWT, logout is typically handled client-side by removing the token.
    For proper logout with token blacklisting, you would need to store tokens in database/redis.
    """
    # In a production app with token blacklisting:
    # - Add current token to blacklist/redis
    # - Set expiration time on blacklist entry
    
    return {"message": "Logged out successfully"}