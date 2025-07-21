from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

from schemas.common import ObjectIdStr, PaginatedResponse


# ---------------------------
# Product Sizes
# ---------------------------

class ProductSizeBase(BaseModel):
    """Base schema for product size."""
    size: str = Field(..., description="Size identifier (e.g., 'S', 'M', 'L', '42', etc.)")
    stock: int = Field(..., ge=0, description="Available quantity in stock")


class ProductSizeCreate(ProductSizeBase):
    """Schema for creating a product size."""
    pass


class ProductSizeUpdate(BaseModel):
    """Schema for updating a product size."""
    size: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)


class ProductSizeOut(ProductSizeBase):
    """Schema for product size in responses."""
    pass


# ---------------------------
# Product Base
# ---------------------------

class ProductBase(BaseModel):
    """Base schema for product."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    category: str
    brand: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_active: bool = Field(default=True)


# ---------------------------
# Product Create / Update
# ---------------------------

class ProductCreate(ProductBase):
    image_urls: List[str] = Field(default_factory=list)
    sizes: List[ProductSizeCreate] = Field(default_factory=list)

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        if round(v, 2) != v:
            raise ValueError("Price must have at most 2 decimal places")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    brand: Optional[str] = None
    image_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("Price must be positive")
            if round(v, 2) != v:
                raise ValueError("Price must have at most 2 decimal places")
        return v


# ---------------------------
# Product Out (Response)
# ---------------------------

class ProductOut(ProductBase):
    """Schema for product in responses."""

    id: ObjectIdStr
    image_urls: List[str] = Field(default_factory=list)
    sizes: List[ProductSizeOut] = Field(default_factory=list)
    created_at: datetime  # ✅ Correct datetime type
    updated_at: Optional[datetime] = None  # ✅ Supports null

    class Config:
        orm_mode = True


# ---------------------------
# Filtering & Pagination
# ---------------------------

class ProductFilter(BaseModel):
    """Schema for filtering products."""
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, gt=0)
    size: Optional[str] = None
    in_stock: Optional[bool] = None
    search: Optional[str] = None
    sort_by: Optional[str] = Field(None, description="Field to sort by (e.g., price, name)")
    sort_order: Optional[str] = Field("asc", description="Sort order (asc or desc)")


class ProductPaginatedResponse(PaginatedResponse):
    """Schema for paginated product response."""
    items: List[ProductOut]
