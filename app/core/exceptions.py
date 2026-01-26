
"""
Custom exception classes for the application.
Provides specific exceptions for different error scenarios.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception class for application errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message=message, status_code=401)


class UnauthorizedError(AppException):
    """Raised when user is not authorized to perform action."""
    
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message=message, status_code=403)


class NotFoundError(AppException):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class AlreadyExistsError(AppException):
    """Raised when trying to create a resource that already exists."""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


class ValidationError(AppException):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details)


class InactiveUserError(AppException):
    """Raised when user account is inactive."""
    
    def __init__(self, message: str = "User account is inactive"):
        super().__init__(message=message, status_code=403)


class UnverifiedUserError(AppException):
    """Raised when user email is not verified."""
    
    def __init__(self, message: str = "Email not verified"):
        super().__init__(message=message, status_code=403)


class InvalidTokenError(AppException):
    """Raised when token is invalid or expired."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message=message, status_code=401)