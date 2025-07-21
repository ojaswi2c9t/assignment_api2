# Create schemas/response.py
response_schema_content = '''"""
Common response schemas for the API.
"""
from typing import Any, List, Optional, Dict, Union
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Standard success response format."""
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "data": {"id": "507f1f77bcf86cd799439011"}
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {"field": "name", "issue": "required field missing"}
            }
        }


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""
    next: Optional[str] = Field(None, description="Next page offset")
    limit: int = Field(..., description="Items per page limit")
    previous: Optional[str] = Field(None, description="Previous page offset")
    
    class Config:
        schema_extra = {
            "example": {
                "next": "10",
                "limit": 10,
                "previous": None
            }
        }


class PaginatedResponse(BaseModel):
    """Generic paginated response format."""
    data: List[Any] = Field(..., description="List of items")
    page: PaginationInfo = Field(..., description="Pagination information")
    total_count: Optional[int] = Field(None, description="Total number of items")
    
    class Config:
        schema_extra = {
            "example": {
                "data": [],
                "page": {
                    "next": "10",
                    "limit": 10,
                    "previous": None
                },
                "total_count": 25
            }
        }


class CreatedResponse(BaseModel):
    """Response for successful creation operations."""
    id: str = Field(..., description="ID of the created resource")
    message: str = Field(default="Resource created successfully", description="Success message")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "message": "Resource created successfully"
            }
        }
'''