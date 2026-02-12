"""
Common schemas used across the application.
Provides standard response formats and error schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ErrorDetail(BaseModel):
    """Error detail schema."""
    field: str = Field(..., description="Field that caused the error")
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str = Field(..., description="Error description")
    errors: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional error details"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Validation error",
                "errors": {
                    "email": "Invalid email format",
                    "password": "Password too short"
                }
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response schema."""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional response data"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "data": {"id": "123e4567-e89b-12d3-a456-426614174000"}
            }
        }


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment (development/production)")
    database: str = Field(..., description="Database status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "app_name": "Task Management API",
                "version": "1.0.0",
                "environment": "development",
                "database": "healthy"
            }
        }


class MetricsResponse(BaseModel):
    """Metrics response schema."""
    uptime: str = Field(..., description="Application uptime")
    total_requests: int = Field(..., description="Total requests processed")
    total_errors: int = Field(..., description="Total errors")
    slowest_endpoints: List[Dict[str, Any]] = Field(
        ...,
        description="Top 10 slowest endpoints"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "uptime": "3600.50 seconds",
                "total_requests": 1234,
                "total_errors": 12,
                "slowest_endpoints": [
                    {
                        "endpoint": "GET /api/v1/tasks",
                        "requests": 450,
                        "avg_time": 0.234,
                        "min_time": 0.100,
                        "max_time": 1.500,
                        "errors": 2
                    }
                ]
            }
        }
