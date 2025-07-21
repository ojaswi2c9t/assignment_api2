from typing import Dict, Any, Optional, List, Union
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import ValidationError


class APIError(Exception):
    """Base API error exception."""
    
    def __init__(
        self, 
        status_code: int, 
        error: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.error = error
        self.message = message
        self.details = details
        super().__init__(self.message)


class NotFoundError(APIError):
    """Resource not found error."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="NotFoundError",
            message=f"{resource_type} with ID {resource_id} not found",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ValidationAPIError(APIError):
    """Validation error."""
    
    def __init__(self, message: str, errors: List[Dict[str, Any]]):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="ValidationError",
            message=message,
            details={"errors": errors}
        )


class DatabaseError(APIError):
    """Database operation error."""
    
    def __init__(self, operation: str, message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="DatabaseError",
            message=f"Database {operation} failed: {message}",
            details={"operation": operation}
        )


class AuthenticationError(APIError):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="AuthenticationError",
            message=message
        )


class AuthorizationError(APIError):
    """Authorization error."""
    
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="AuthorizationError",
            message=message
        )


def format_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format validation errors for API response."""
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    return formatted_errors


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Validation error",
            "details": {"errors": format_validation_errors(exc.errors())},
            "path": request.url.path
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": request.url.path
        }
    ) 