from typing import Generic, TypeVar, List, Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field, BeforeValidator
from pydantic.generics import GenericModel


# Generic type for paginated responses
T = TypeVar('T')


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    
    page: int = Field(1, ge=1, description="Page number, starting from 1")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")
    
    @property
    def skip(self) -> int:
        """Calculate skip value for MongoDB query."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Return limit value for MongoDB query."""
        return self.page_size


class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""
    
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")
    
    @classmethod
    def create(cls, params: PaginationParams, total_items: int) -> "PaginationMeta":
        """Create pagination metadata."""
        total_pages = (total_items + params.page_size - 1) // params.page_size if total_items > 0 else 0
        
        return cls(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=params.page > 1,
            has_next=params.page < total_pages
        )


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic paginated response."""
    
    items: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    
    @classmethod
    def create(cls, items: List[T], params: PaginationParams, total_items: int) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        return cls(
            items=items,
            meta=PaginationMeta.create(params, total_items)
        )


class MessageResponse(BaseModel):
    """Simple message response."""
    
    message: str = Field(..., description="Response message")


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")


def validate_object_id(v: Any) -> str:
    """Validate that a string is a valid MongoDB ObjectId."""
    from bson import ObjectId
    
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return str(v)


# Define ObjectIdStr as an Annotated type
ObjectIdStr = Annotated[str, BeforeValidator(validate_object_id)] 