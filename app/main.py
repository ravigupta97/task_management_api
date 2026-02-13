"""
Main FastAPI application.
Initializes app, middleware, routes, and exception handlers.
"""

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.api.v1 import api_router
from app.core.exceptions import AppException
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.database import engine
import logging
import time
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log") if not settings.DEBUG else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await engine.dispose()


# Create FastAPI app with enhanced documentation
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Task Management API

A production-ready REST API for task and project management.

### Features

* **Authentication**: JWT-based authentication with access and refresh tokens
* **User Management**: Complete user profile management
* **Tasks**: Full CRUD operations with advanced filtering and search
* **Categories**: Organize tasks into custom categories
* **Rate Limiting**: Protection against abuse and brute force attacks
* **Performance Monitoring**: Track API performance and identify bottlenecks

### Security

All endpoints (except authentication and public endpoints) require a valid JWT token.

Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

### Rate Limits

Different endpoints have different rate limits to prevent abuse:

- Authentication endpoints: 3-10 requests/minute
- Standard endpoints: 30-100 requests/minute
- Health/metrics: 10 requests/minute

Rate limit info is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: Time when the limit resets

### Response Headers

All responses include:
- `X-Process-Time`: Request processing time in seconds
- Rate limit headers (when applicable)

### Error Responses

All errors follow a consistent format:
```json
{
  "detail": "Error description",
  "errors": {
    "field": "Specific error message"
  }
}
```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        409: {"description": "Conflict"},
        422: {"description": "Validation Error"},
        429: {"description": "Too Many Requests"},
        500: {"description": "Internal Server Error"},
        503: {"description": "Service Unavailable"}
    },
    contact={
        "name": "API Support",
        "email": "support@taskmanagement.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)



# Custom exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "errors": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "errors": {}
        }
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return rate_limit_exceeded_handler(request, exc)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "errors": {}
        }
    )

# Add rate limiter to app state
app.state.limiter = limiter
# Add exception handler for rate limit
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# CORS middleware (must be added BEFORE other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging and monitoring middleware
@app.middleware("http")
async def log_and_monitor_requests(request: Request, call_next):
    """
    Log all incoming requests, track performance, and add timing headers.
    """
    from app.core.monitoring import performance_monitor
    
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Record metrics
        performance_monitor.record_request(
            endpoint=f"{request.method} {request.url.path}",
            duration=process_time,
            status_code=response.status_code
        )
        
        # Add headers
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        # Warn on slow requests (> 1 second)
        if process_time > 1.0:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {process_time:.4f}s"
            )
        
        return response
    
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error processing request: {str(e)}")
        
        # Record error
        performance_monitor.record_request(
            endpoint=f"{request.method} {request.url.path}",
            duration=process_time,
            status_code=500
        )
        
        raise

# Include API router
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["Health"])
@limiter.limit("10/minute")  # Custom rate limit for health checks
async def health_check(request: Request, response: Response,):
    """
    Health check endpoint with database connectivity test.
    Returns API status, version, and database status.
    """
    from sqlalchemy import text
    
    db_status = "healthy"
    try:
        # Test database connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {str(e)}")
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }

# Metrics endpoint for monitoring
@app.get("/metrics", tags=["Monitoring"])
@limiter.limit("10/minute")
async def get_metrics(request: Request, response: Response,):
    """
    Get API performance metrics.
    
    **Rate limit: 10 requests per minute**
    
    Returns:
    - Uptime
    - Total requests processed
    - Total errors
    - Top 10 slowest endpoints with stats
    """
    from app.core.monitoring import performance_monitor
    
    stats = performance_monitor.get_stats()
    
    return {
        "uptime": f"{stats['uptime_seconds']:.2f} seconds",
        "total_requests": stats["total_requests"],
        "total_errors": stats["total_errors"],
        "slowest_endpoints": stats["endpoints"]
    }


# Reset metrics endpoint (admin only - in production, add authentication)
@app.post("/metrics/reset", tags=["Monitoring"])
@limiter.limit("1/hour")
async def reset_metrics(request: Request, response: Response,):
    """
    Reset performance metrics.
    
    **Rate limit: 1 request per hour**
    
    ⚠️ In production, this should require admin authentication.
    """
    from app.core.monitoring import performance_monitor
    
    performance_monitor.reset()
    
    return {"message": "Metrics reset successfully"}


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

