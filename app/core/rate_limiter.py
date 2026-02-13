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
    # Get forwarded IP (for when behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    
    # Fallback to direct IP
    return get_remote_address(request)


# Initialize limiter with swallow_errors=True for production
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["100/minute"],
    storage_uri="memory://",
    strategy="fixed-window",
    headers_enabled=True,
    swallow_errors=True,  # Don't crash on rate limit errors
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
            "retry_after": str(exc.detail) if exc.detail else "60"
        },
        headers={
            "Retry-After": str(exc.detail) if exc.detail else "60"
        }
    )