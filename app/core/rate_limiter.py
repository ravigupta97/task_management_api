
"""
Rate limiting configuration using SlowAPI.
Protects endpoints from abuse and brute force attacks.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


def get_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    
    Uses remote address as default, but can be extended to use
    user ID for authenticated requests.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Identifier string for rate limiting
    """
    # For authenticated requests, you could use user ID
    # if hasattr(request.state, "user"):
    #     return f"user:{request.state.user.id}"
    
    # Default: use IP address
    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["100/minute"],  # Global default limit
    storage_uri="memory://",  # In-memory storage (use Redis in production)
    strategy="fixed-window",  # Rate limiting strategy
    headers_enabled=True,  # Include rate limit info in response headers
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        request: FastAPI request
        exc: RateLimitExceeded exception
        
    Returns:
        JSON response with rate limit info
    """
    logger.warning(
        f"Rate limit exceeded for {get_identifier(request)} on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": exc.detail
        },
        headers={
            "Retry-After": str(exc.detail)
        }
    )