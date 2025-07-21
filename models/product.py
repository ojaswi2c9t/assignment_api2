# Create models/product.py
product_model_content = '''"""
Product data models for MongoDB.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument, TimestampMixin


class ProductSize(BaseModel):
    """Product size model."""
    size: str = Field(..., description="Size name (e.g., 'large', 'medium', 'small')")
    quantity: int = Field(default=0, ge=0, description="Available quantity for this size")
    
    class Config:
        schema_extra = {
            "example": {
                "size": "large",
                "quantity": 100
            }
        }


class Product(BaseDocument, TimestampMixin):
    """Product document model for MongoDB."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    price: float = Field(..., gt=0, description="Product price")
    sizes: List[ProductSize] = Field(default_factory=list, description="Available sizes and quantities")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Premium Cotton T-Shirt",
                "price": 29.99,
                "sizes": [
                    {"size": "small", "quantity": 50},
                    {"size": "medium", "quantity": 75},
                    {"size": "large", "quantity": 100}
                ]
            }
        }


# MongoDB collection helper functions
def product_helper(product: dict) -> dict:
    """Helper function to convert MongoDB document to dict."""
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "price": product["price"],
        "sizes": product.get("sizes", [])
    }
'''

with open("ecommerce_api/models/product.py", "w") as f:
    f.write(product_model_content)

print("✅ models/product.py created")

# Create schemas/product.py
product_schema_content = '''"""
Pydantic schemas for product API validation and serialization.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ProductSizeSchema(BaseModel):
    """Schema for product size."""
    size: str = Field(..., min_length=1, max_length=50, description="Size name")
    quantity: int = Field(default=0, ge=0, description="Available quantity")
    
    class Config:
        schema_extra = {
            "example": {
                "size": "large",
                "quantity": 100
            }
        }


class ProductCreateSchema(BaseModel):
    """Schema for creating a new product."""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    price: float = Field(..., gt=0, description="Product price")
    sizes: List[ProductSizeSchema] = Field(..., min_items=1, description="Product sizes and quantities")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()
    
    @validator('sizes')
    def validate_sizes(cls, v):
        if not v:
            raise ValueError('At least one size must be provided')
        
        # Check for duplicate sizes
        sizes = [size.size.lower() for size in v]
        if len(sizes) != len(set(sizes)):
            raise ValueError('Duplicate sizes are not allowed')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Premium Cotton T-Shirt",
                "price": 29.99,
                "sizes": [
                    {"size": "small", "quantity": 50},
                    {"size": "medium", "quantity": 75},
                    {"size": "large", "quantity": 100}
                ]
            }
        }


class ProductResponseSchema(BaseModel):
    """Schema for product response."""
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    sizes: List[ProductSizeSchema] = Field(..., description="Product sizes")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Premium Cotton T-Shirt",
                "price": 29.99,
                "sizes": [
                    {"size": "small", "quantity": 50},
                    {"size": "medium", "quantity": 75},
                    {"size": "large", "quantity": 100}
                ]
            }
        }


class ProductListResponseSchema(BaseModel):
    """Schema for product list response with pagination."""
    data: List[ProductResponseSchema] = Field(..., description="List of products")
    page: dict = Field(..., description="Pagination information")
    
    class Config:
        schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "name": "Premium Cotton T-Shirt",
                        "price": 29.99,
                        "sizes": [{"size": "large", "quantity": 100}]
                    }
                ],
                "page": {
                    "next": "10",
                    "limit": 0,
                    "previous": "-10"
                }
            }
        }


class ProductUpdateSchema(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    price: Optional[float] = Field(None, gt=0, description="Product price")
    sizes: Optional[List[ProductSizeSchema]] = Field(None, description="Product sizes")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip() if v else v
    
    @validator('sizes')
    def validate_sizes(cls, v):
        if v is not None:
            # Check for duplicate sizes
            sizes = [size.size.lower() for size in v]
            if len(sizes) != len(set(sizes)):
                raise ValueError('Duplicate sizes are not allowed')
        return v
'''

with open("ecommerce_api/schemas/product.py", "w") as f:
    f.write(product_schema_content)

print("✅ schemas/product.py created")