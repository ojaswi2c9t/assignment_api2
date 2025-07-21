# models/order_v2.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field, BaseModel, field_validator
from bson import ObjectId
from core.database import get_collection


# Helper to convert ObjectId to str
def order_helper(order_doc: Dict[str, Any]) -> Dict[str, Any]:
    # Process order items to ensure they have required fields
    items = order_doc.get("items", [])
    processed_items = []
    
    for item in items:
        processed_item = dict(item)
        # Ensure each item has product_name, price, and subtotal
        if "product_name" not in processed_item:
            processed_item["product_name"] = processed_item.get("name", "Unknown Product")
        
        if "price" not in processed_item:
            processed_item["price"] = float(processed_item.get("unit_price", 0))
        
        if "subtotal" not in processed_item:
            quantity = int(processed_item.get("quantity", 1))
            price = float(processed_item.get("price", 0))
            processed_item["subtotal"] = round(quantity * price, 2)
            
        processed_items.append(processed_item)
    
    # Format datetime objects as strings
    created_at = order_doc.get("created_at")
    if created_at and isinstance(created_at, datetime):
        created_at = created_at.isoformat()
        
    updated_at = order_doc.get("updated_at")
    if updated_at and isinstance(updated_at, datetime):
        updated_at = updated_at.isoformat()
    
    # Check for status fields
    order_status = order_doc.get("order_status")
    if order_status is None:
        # Try to get from status field for backward compatibility
        order_status = order_doc.get("status", "pending")
        
    payment_status = order_doc.get("payment_status", "pending")
    
    return {
        "id": str(order_doc.get("_id", "")),
        "user_id": order_doc.get("user_id"),
        "items": processed_items,
        "shipping_address": order_doc.get("shipping_address", {}),
        "order_status": order_status,
        "payment_status": payment_status,
        "subtotal": order_doc.get("subtotal", 0.0),
        "shipping_cost": order_doc.get("shipping_cost", 0.0),
        "tax": order_doc.get("tax", 0.0),
        "total": order_doc.get("total", order_doc.get("total_amount", 0.0)),
        "tracking_number": order_doc.get("tracking_number"),
        "notes": order_doc.get("notes"),
        "created_at": created_at,
        "updated_at": updated_at,
    }


def get_order_lookup_pipeline(user_id: str, limit: int, offset: int) -> List[dict]:
    return [
        {"$match": {"user_id": user_id}},
        {
            "$lookup": {
                "from": "products",
                "localField": "items.product_id",
                "foreignField": "_id",
                "as": "product_details"
            }
        },
        {"$sort": {"_id": 1}},
        {"$skip": offset},
        {"$limit": limit},
    ]


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class TimestampedModel(BaseModel):
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    model_config = {
        "arbitrary_types_allowed": True
    }


class OrderItem(TimestampedModel):
    product_id: str = Field(...)
    product_name: str
    size: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

    @property
    def subtotal(self) -> float:
        return round(self.price * self.quantity, 2)


class ShippingAddress(TimestampedModel):
    full_name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None


class Order(TimestampedModel):
    user_id: Optional[str] = None
    items: List[OrderItem]
    shipping_address: ShippingAddress
    order_status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    subtotal: float
    shipping_cost: float = 0.0
    tax: float = 0.0
    total: float
    tracking_number: Optional[str] = None
    notes: Optional[str] = None

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v or len(v) < 1:
            raise ValueError("Order must have at least one item")
        return v

    @field_validator('total')
    @classmethod
    def validate_total(cls, v, info):
        values = info.data
        if 'subtotal' in values and 'shipping_cost' in values and 'tax' in values:
            expected_total = round(values['subtotal'] + values['shipping_cost'] + values['tax'], 2)
            if abs(v - expected_total) > 0.01:
                raise ValueError(f"Total {v} does not match expected {expected_total}")
        return v

    @classmethod
    async def get_by_id(cls, db, order_id: str):
        if not ObjectId.is_valid(order_id):
            return None
        order_data = await get_collection("orders").find_one({"_id": ObjectId(order_id)})
        return cls(**order_data) if order_data else None

    @classmethod
    async def create(cls, db, order_data: dict):
        order = cls(**order_data)
        order_dict = order.model_dump(by_alias=True)
        result = await get_collection("orders").insert_one(order_dict)
        order_dict["_id"] = result.inserted_id
        return order_helper(order_dict)  # Return serializable version

    @classmethod
    async def update_status(cls, db, order_id: str, order_status: str, payment_status: Optional[str] = None):
        if not ObjectId.is_valid(order_id):
            return None
        update_data = {
            "order_status": order_status,
            "updated_at": datetime.utcnow()
        }
        if payment_status:
            update_data["payment_status"] = payment_status
        await get_collection("orders").update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        return await cls.get_by_id(db, order_id) 