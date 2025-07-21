# Create routes/products.py
products_routes_content = '''"""
Product API routes.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse

from ..schemas.product import (
    ProductCreateSchema, 
    ProductResponseSchema, 
    ProductListResponseSchema,
    ProductUpdateSchema
)
from ..schemas.response import SuccessResponse, CreatedResponse, ErrorResponse
from ..services.product_service import product_service
from ..utils.pagination import PaginationParams
from ..utils.helpers import log_api_call

router = APIRouter()


@router.post(
    "/", 
    response_model=CreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product with name, price, and sizes information."
)
async def create_product(product: ProductCreateSchema):
    """
    Create a new product.
    
    - **name**: Product name (required, 1-255 characters)
    - **price**: Product price (required, must be positive)
    - **sizes**: List of available sizes with quantities (required, at least one)
    
    Returns the created product ID.
    """
    try:
        log_api_call("/products", "POST")
        
        # Convert Pydantic model to dict
        product_data = product.dict()
        
        # Create product
        created_product = await product_service.create_product(product_data)
        
        return CreatedResponse(
            id=created_product["id"],
            message="Product created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=ProductListResponseSchema,
    summary="List products with filtering and pagination",
    description="Get a list of products with optional filtering by name and size, plus pagination support."
)
async def get_products(
    name: Optional[str] = Query(None, description="Filter by product name (partial match)"),
    size: Optional[str] = Query(None, description="Filter by available size (e.g., 'large')"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    offset: int = Query(0, ge=0, description="Number of items to skip for pagination")
):
    """
    Get products with optional filtering and pagination.
    
    **Query Parameters:**
    - **name**: Filter products by name (case-insensitive partial match)
    - **size**: Filter products that have the specified size available
    - **limit**: Number of products to return (1-100, default: 10)
    - **offset**: Number of products to skip for pagination (default: 0)
    
    **Response includes:**
    - List of products with their details
    - Pagination information for navigation
    """
    try:
        log_api_call("/products", "GET", name=name, size=size, limit=limit, offset=offset)
        
        # Get products from service
        products, pagination_info = await product_service.get_products(
            name=name,
            size=size,
            limit=limit,
            offset=offset
        )
        
        return ProductListResponseSchema(
            data=products,
            page=pagination_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{product_id}",
    response_model=ProductResponseSchema,
    summary="Get a specific product",
    description="Retrieve a single product by its ID."
)
async def get_product(product_id: str):
    """
    Get a specific product by ID.
    
    - **product_id**: MongoDB ObjectId of the product (24-character hex string)
    
    Returns detailed product information including all sizes and quantities.
    """
    try:
        log_api_call(f"/products/{product_id}", "GET")
        
        # Get product from service
        product = await product_service.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ProductResponseSchema(**product)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/{product_id}",
    response_model=SuccessResponse,
    summary="Update a product",
    description="Update an existing product's information."
)
async def update_product(product_id: str, product: ProductUpdateSchema):
    """
    Update a product.
    
    - **product_id**: MongoDB ObjectId of the product to update
    - **product**: Product data to update (all fields are optional)
    
    Only provided fields will be updated. Other fields remain unchanged.
    """
    try:
        log_api_call(f"/products/{product_id}", "PUT")
        
        # Convert Pydantic model to dict, excluding None values
        update_data = product.dict(exclude_none=True)
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        # Update product
        success = await product_service.update_product(product_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return SuccessResponse(
            message="Product updated successfully",
            data={"id": product_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{product_id}",
    response_model=SuccessResponse,
    summary="Delete a product",
    description="Delete a product by its ID."
)
async def delete_product(product_id: str):
    """
    Delete a product.
    
    - **product_id**: MongoDB ObjectId of the product to delete
    
    This operation cannot be undone.
    """
    try:
        log_api_call(f"/products/{product_id}", "DELETE")
        
        # Delete product
        success = await product_service.delete_product(product_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return SuccessResponse(
            message="Product deleted successfully",
            data={"id": product_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/search/{search_term}",
    response_model=list[ProductResponseSchema],
    summary="Search products",
    description="Search products by name using text search."
)
async def search_products(
    search_term: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    Search products by name.
    
    - **search_term**: Text to search for in product names
    - **limit**: Maximum number of results to return (1-50, default: 10)
    
    Returns a list of products that match the search term.
    """
    try:
        log_api_call(f"/products/search/{search_term}", "GET", limit=limit)
        
        # Search products
        products = await product_service.search_products(search_term, limit)
        
        return products
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Error handlers for this router
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions for product routes."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "ProductError",
            "message": exc.detail,
            "endpoint": str(request.url)
        }
    )


@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors for product routes."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "message": str(exc),
            "endpoint": str(request.url)
        }
    )
'''

with open("ecommerce_api/routes/products.py", "w") as f:
    f.write(products_routes_content)

print("✅ routes/products.py created")