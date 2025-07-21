from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from typing import List, Optional
from bson import ObjectId

from core.database import get_database
from schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductOut, 
    ProductFilter, 
    ProductPaginatedResponse
)
from schemas.common import MessageResponse
from schemas.pagination import PaginationParams
from services.product_service import ProductService


router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db = Depends(get_database)
):
    """Create a new product."""
    product_service = ProductService(db)
    return await product_service.create_product(product)


@router.get("/", response_model=ProductPaginatedResponse)
async def list_products(
    pagination: PaginationParams = Depends(),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    size: Optional[str] = None,
    in_stock: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    db = Depends(get_database)
):
    """
    Get a paginated list of products with optional filtering.
    
    - **pagination**: Pagination parameters
    - **category**: Filter by category
    - **brand**: Filter by brand
    - **min_price**: Filter by minimum price
    - **max_price**: Filter by maximum price
    - **size**: Filter by available size
    - **in_stock**: Filter by in-stock status
    - **search**: Search in name and description
    - **sort_by**: Field to sort by (name, price, created_at)
    - **sort_order**: Sort order (asc or desc)
    """
    product_service = ProductService(db)
    
    # Create filter from query params
    filter_params = ProductFilter(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        size=size,
        in_stock=in_stock,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return await product_service.list_products(pagination, filter_params)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: str = Path(..., title="The ID of the product to get"),
    db = Depends(get_database)
):
    """Get a product by ID."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
        
    product_service = ProductService(db)
    product = await product_service.get_product(product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_update: ProductUpdate,
    product_id: str = Path(..., title="The ID of the product to update"),
    db = Depends(get_database)
):
    """Update a product."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
        
    product_service = ProductService(db)
    product = await product_service.update_product(product_id, product_update)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    return product


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: str = Path(..., title="The ID of the product to delete"),
    db = Depends(get_database)
):
    """Delete a product."""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID format"
        )
        
    product_service = ProductService(db)
    deleted = await product_service.delete_product(product_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    return MessageResponse(message=f"Product {product_id} deleted successfully") 