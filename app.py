import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="E-Commerce API",
    description="E-Commerce API with FastAPI and MongoDB",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root() -> Dict[str, str]:
    return {
        "message": "Welcome to E-Commerce API!",
        "docs_url": "/api/docs",
        "health_endpoint": "/health"
    }

# Health check
@app.get("/health", include_in_schema=False)
async def health() -> Dict[str, str]:
    return {"status": "healthy"}

# Mock product data
PRODUCTS = [
    {
        "id": "1",
        "name": "Sample T-Shirt",
        "description": "A test product.",
        "price": 499.99,
        "category": "apparel",
        "brand": "TestBrand",
        "tags": ["tshirt", "sample"],
        "is_active": True,
        "image_urls": [],
        "sizes": [
            {"size": "M", "stock": 50},
            {"size": "L", "stock": 35}
        ],
        "created_at": "2025-07-20T05:42:00.057000",
        "updated_at": "2025-07-20T05:42:00.057000"
    }
]

# Mock orders data
ORDERS = []

# Product endpoints
@app.post("/api/v1/products", status_code=201)
async def create_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new product."""
    # Add timestamp
    from datetime import datetime
    product["created_at"] = datetime.utcnow().isoformat()
    product["updated_at"] = datetime.utcnow().isoformat()
    
    # Add ID
    import uuid
    product["id"] = str(uuid.uuid4())
    
    # Add to mock database
    PRODUCTS.append(product)
    
    return product

@app.get("/api/v1/products")
async def list_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    size: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 10,
    skip: int = 0
) -> Dict[str, Any]:
    """Get a list of products with optional filtering."""
    # Filter products
    filtered_products = PRODUCTS
    
    if category:
        filtered_products = [p for p in filtered_products if p.get("category") == category]
    if brand:
        filtered_products = [p for p in filtered_products if p.get("brand") == brand]
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p.get("price", 0) >= min_price]
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p.get("price", 0) <= max_price]
    if size:
        filtered_products = [p for p in filtered_products if any(s.get("size") == size for s in p.get("sizes", []))]
    if search:
        import re
        pattern = re.compile(search, re.IGNORECASE)
        filtered_products = [
            p for p in filtered_products 
            if pattern.search(p.get("name", "")) or pattern.search(p.get("description", ""))
        ]
    
    # Apply pagination
    paginated_products = filtered_products[skip:skip + limit]
    
    # Return paginated response
    return {
        "items": paginated_products,
        "total": len(filtered_products),
        "limit": limit,
        "skip": skip
    }

@app.get("/api/v1/products/{product_id}")
async def get_product(product_id: str) -> Dict[str, Any]:
    """Get a product by ID."""
    # Find product by ID
    for product in PRODUCTS:
        if product.get("id") == product_id:
            return product
    
    # Return 404 if not found
    raise HTTPException(status_code=404, detail="Product not found")

# Order endpoints
@app.post("/api/v1/orders", status_code=201)
async def create_order(order: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new order."""
    # Add timestamp
    from datetime import datetime
    order["created_at"] = datetime.utcnow().isoformat()
    order["updated_at"] = datetime.utcnow().isoformat()
    
    # Add ID
    import uuid
    order["id"] = str(uuid.uuid4())
    
    # Calculate subtotal, tax, and total
    subtotal = 0
    for item in order.get("items", []):
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)
        
        # Find product
        product = None
        for p in PRODUCTS:
            if p.get("id") == product_id:
                product = p
                break
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product not found: {product_id}")
        
        # Add product details to item
        item["product_name"] = product.get("name", "Unknown Product")
        item["price"] = product.get("price", 0)
        item["subtotal"] = item["price"] * quantity
        
        # Add to subtotal
        subtotal += item["subtotal"]
    
    # Set order totals
    order["subtotal"] = subtotal
    order["shipping_cost"] = order.get("shipping_cost", 0)
    order["tax"] = order.get("tax", 0)
    order["total"] = subtotal + order["shipping_cost"] + order["tax"]
    
    # Set status
    order["order_status"] = "pending"
    order["payment_status"] = "pending"
    
    # Add to mock database
    ORDERS.append(order)
    
    return order

@app.get("/api/v1/orders")
async def list_orders(
    user_id: Optional[str] = None,
    limit: int = 10,
    skip: int = 0
) -> Dict[str, Any]:
    """Get a list of orders with optional filtering."""
    # Filter orders
    filtered_orders = ORDERS
    
    if user_id:
        filtered_orders = [o for o in filtered_orders if o.get("user_id") == user_id]
    
    # Apply pagination
    paginated_orders = filtered_orders[skip:skip + limit]
    
    # Return paginated response
    return {
        "items": paginated_orders,
        "total": len(filtered_orders),
        "limit": limit,
        "skip": skip
    }

@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str) -> Dict[str, Any]:
    """Get an order by ID."""
    # Find order by ID
    for order in ORDERS:
        if order.get("id") == order_id:
            return order
    
    # Return 404 if not found
    raise HTTPException(status_code=404, detail="Order not found") 