import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException

from utils.helpers import convert_objectid, calculate_total_amount, ValidationHelper
from models.order import order_helper, get_order_lookup_pipeline, OrderStatus, PaymentStatus
from schemas.order import OrderFilter
from schemas.pagination import PaginationParams, PaginatedResponse
from services.product_service import ProductService

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, db):
        self.db = db
        self.collection = db["orders"]
        self.product_service = ProductService(db)

    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            validated_data = ValidationHelper.validate_order_data(order_data)
            product_ids = [item["product_id"] for item in validated_data["items"]]
            existing_products, missing_ids = await self.product_service.check_products_exist(product_ids)

            if missing_ids:
                raise HTTPException(
                    status_code=404,
                    detail=f"Products not found: {', '.join(missing_ids)}"
                )

            # Create a map of products for easy lookup
            product_map = {str(p["_id"]): p for p in existing_products}
            
            # Enrich order items with product information
            subtotal = 0.0
            for item in validated_data["items"]:
                product = product_map.get(item["product_id"])
                if product:
                    item["product_name"] = product.get("name", "Unknown Product")
                    item["price"] = float(product.get("price", 0))
                    item["subtotal"] = round(item["price"] * item["quantity"], 2)
                    subtotal += item["subtotal"]
            
            # Set order totals
            validated_data["subtotal"] = subtotal
            validated_data["shipping_cost"] = validated_data.get("shipping_cost", 0.0)
            validated_data["tax"] = validated_data.get("tax", 0.0)
            validated_data["total"] = round(subtotal + validated_data["shipping_cost"] + validated_data["tax"], 2)
            validated_data["order_status"] = OrderStatus.PENDING
            validated_data["payment_status"] = PaymentStatus.PENDING
            validated_data["created_at"] = datetime.utcnow()
            validated_data["updated_at"] = None

            result = await self.collection.insert_one(validated_data)
            if not result.inserted_id:
                raise HTTPException(status_code=500, detail="Failed to create order")

            created_order = await self.collection.find_one({"_id": result.inserted_id})
            return order_helper(created_order)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def list_orders(
        self,
        pagination: PaginationParams,
        filters: OrderFilter
    ) -> PaginatedResponse:
        try:
            query: Dict[str, Any] = {}

            if filters.user_id:
                query["user_id"] = filters.user_id

            if filters.order_status:
                query["status"] = filters.order_status

            if filters.payment_status:
                query["payment_status"] = filters.payment_status

            if filters.min_total is not None:
                query["total_amount"] = query.get("total_amount", {})
                query["total_amount"]["$gte"] = filters.min_total

            if filters.max_total is not None:
                query["total_amount"] = query.get("total_amount", {})
                query["total_amount"]["$lte"] = filters.max_total

            if filters.date_from or filters.date_to:
                query["created_at"] = {}
                if filters.date_from:
                    query["created_at"]["$gte"] = filters.date_from
                if filters.date_to:
                    query["created_at"]["$lte"] = filters.date_to

            total_items = await self.collection.count_documents(query)

            cursor = (
                self.collection.find(query)
                .sort("created_at", -1)
                .skip(pagination.skip)
                .limit(pagination.limit)
            )

            orders: List[Dict[str, Any]] = []
            async for doc in cursor:
                orders.append(order_helper(doc))

            return PaginatedResponse.create(
                items=orders,
                params=pagination,
                total_items=total_items
            )

        except Exception as e:
            logger.error(f"Error listing orders: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def get_order_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        try:
            object_id = convert_objectid(order_id)
            order = await self.collection.find_one({"_id": object_id})
            return order_helper(order) if order else None
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def update_order_status(self, order_id: str, status: str) -> bool:
        try:
            object_id = convert_objectid(order_id)
            valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": {"status": status, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating order status {order_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete_order(self, order_id: str) -> bool:
        try:
            return await self.update_order_status(order_id, "cancelled")
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
