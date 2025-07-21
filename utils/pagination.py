from typing import Dict, List, Any, Tuple, TypeVar, Generic, Optional
from math import ceil


T = TypeVar('T')


class Paginator:
    """Helper class for pagination."""
    
    def __init__(self, page: int = 1, page_size: int = 10):
        """Initialize paginator with page and page_size."""
        self.page = max(1, page)  # Ensure page is at least 1
        self.page_size = min(max(1, page_size), 100)  # Ensure page_size is between 1 and 100
    
    @property
    def skip(self) -> int:
        """Calculate skip value for database query."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Return limit value for database query."""
        return self.page_size
    
    def get_pagination_metadata(self, total_items: int) -> Dict[str, Any]:
        """Generate pagination metadata."""
        total_pages = ceil(total_items / self.page_size) if total_items > 0 else 0
        
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_previous": self.page > 1,
            "has_next": self.page < total_pages
        }
    
    def paginate_data(self, data: List[T], total_items: int) -> Tuple[List[T], Dict[str, Any]]:
        """Paginate data and return with metadata."""
        metadata = self.get_pagination_metadata(total_items)
        return data, metadata


def get_pagination_params(page: int = 1, page_size: int = 10) -> Dict[str, int]:
    """Get pagination parameters for database query."""
    page = max(1, page)  # Ensure page is at least 1
    page_size = min(max(1, page_size), 100)  # Ensure page_size is between 1 and 100
    
    return {
        "skip": (page - 1) * page_size,
        "limit": page_size
    }


def create_paginated_response(
    items: List[T], 
    page: int, 
    page_size: int, 
    total_items: int
) -> Dict[str, Any]:
    """Create a standardized paginated response."""
    total_pages = ceil(total_items / page_size) if total_items > 0 else 0
    
    return {
        "items": items,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages
        }
    }


def create_pagination_info(
    limit: int,
    offset: int,
    total_count: Optional[int] = None,
    has_more: bool = False
) -> Dict[str, Any]:
    """
    Create pagination information for responses.
    Args:
        limit: Items per page
        offset: Current offset
        total_count: Total number of items (optional)
        has_more: Whether there are more items available
    Returns:
        Dictionary with pagination information
    """
    pagination = {
        "limit": limit,
        "next": None,
        "previous": None
    }
    # Calculate next page
    if has_more or (total_count and (offset + limit) < total_count):
        pagination["next"] = str(offset + limit)
    # Calculate previous page
    if offset > 0:
        prev_offset = max(0, offset - limit)
        pagination["previous"] = str(prev_offset) if prev_offset > 0 else "0"
    return pagination
