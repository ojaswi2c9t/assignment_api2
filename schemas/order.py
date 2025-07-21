from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from schemas.common import ObjectIdStr, PaginatedResponse
from models.order import OrderStatus, PaymentStatus


class ShippingAddressBase(BaseModel):
    """Base schema for shipping address."""
    
    full_name: str = Field(..., min_length=1)
    address_line1: str = Field(..., min_length=1)
    address_line2: Optional[str] = None
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    postal_code: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    phone: Optional[str] = None


class OrderItemBase(BaseModel):
    """Base schema for order item."""
    
    product_id: str = Field(..., description="Product ID")
    size: str = Field(..., description="Product size")
    quantity: int = Field(..., gt=0, description="Quantity of items")


class OrderItemCreate(OrderItemBase):
    """Schema for creating an order item."""
    pass


class OrderItemOut(OrderItemBase):
    """Schema for order item in responses."""
    
    product_name: str
    price: float
    subtotal: float
    
    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    
    user_id: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_items=1)
    shipping_address: ShippingAddressBase
    notes: Optional[str] = None
    
    @validator('items')
    def validate_items(cls, v):
        """Validate that order has at least one item."""
        if not v or len(v) < 1:
            raise ValueError("Order must have at least one item")
        return v


class OrderUpdate(BaseModel):
    """Schema for updating an order."""
    
    order_status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None


class OrderOut(BaseModel):
    """Schema for order in responses."""
    
    id: ObjectIdStr
    user_id: Optional[str] = None
    items: List[OrderItemOut]
    shipping_address: ShippingAddressBase
    order_status: OrderStatus
    payment_status: PaymentStatus
    subtotal: float
    shipping_cost: float
    tax: float
    total: float
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        orm_mode = True


class OrderFilter(BaseModel):
    """Schema for filtering orders."""
    
    user_id: Optional[str] = None
    order_status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    min_total: Optional[float] = Field(None, ge=0)
    max_total: Optional[float] = Field(None, gt=0)
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class OrderPaginatedResponse(PaginatedResponse):
    """Schema for paginated order response."""
    
    items: List[OrderOut] 