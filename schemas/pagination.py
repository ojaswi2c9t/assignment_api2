from typing import Generic, TypeVar, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

# Generic type for paginated responses
T = TypeVar('T')


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = Field(1, ge=1, description="Page number, starting from 1")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")

    @property
    def skip(self) -> int:
        """Offset to be used in MongoDB skip()."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Limit to be used in MongoDB limit()."""
        return self.page_size

    def to_mongo_query(self) -> Dict[str, int]:
        """Convert pagination parameters to MongoDB query options."""
        return {
            "skip": self.skip,
            "limit": self.limit
        }


class PaginationMeta(BaseModel):
    """Metadata for paginated responses."""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool

    @classmethod
    def create(cls, params: PaginationParams, total_items: int) -> "PaginationMeta":
        total_pages = (total_items + params.page_size - 1) // params.page_size if total_items > 0 else 1

        return cls(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=params.page > 1,
            has_next=params.page < total_pages
        )


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic paginated API response wrapper."""
    items: List[T]
    meta: PaginationMeta

    @classmethod
    def create(cls, items: List[T], params: PaginationParams, total_items: int) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            meta=PaginationMeta.create(params, total_items)
        )
