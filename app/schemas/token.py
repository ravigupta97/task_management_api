
"""
Pydantic schemas for authentication tokens.
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Response schema for login endpoint."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""
    sub: Optional[str] = None  # Subject (user_id)
    exp: Optional[int] = None  # Expiration timestamp
    type: Optional[str] = None  # Token type


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response schema for token refresh."""
    access_token: str
    token_type: str = "bearer"