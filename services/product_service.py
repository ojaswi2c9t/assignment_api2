from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.product import ProductCreate, ProductUpdate, ProductFilter
from schemas.pagination import PaginationParams, PaginatedResponse


class ProductService:
    """Service for product-related operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.products

    async def create_product(self, product: ProductCreate) -> Dict[str, Any]:
        product_dict = product.dict()
        now = datetime.utcnow()
        product_dict["created_at"] = now
        product_dict["updated_at"] = now

        result = await self.collection.insert_one(product_dict)
        created_product = await self.collection.find_one({"_id": result.inserted_id})
        created_product["id"] = str(created_product.pop("_id"))
        return created_product

    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(product_id):
            return None
        product = await self.collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return None
        product["id"] = str(product.pop("_id"))
        product["created_at"] = product["created_at"].isoformat()
        product["updated_at"] = product["updated_at"].isoformat() if product["updated_at"] else None
        return product

    async def update_product(self, product_id: str, product_update: ProductUpdate) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(product_id):
            return None
        update_data = {k: v for k, v in product_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
        if result.matched_count == 0:
            return None
        return await self.get_product(product_id)

    async def delete_product(self, product_id: str) -> bool:
        if not ObjectId.is_valid(product_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0

    async def list_products(self, pagination: PaginationParams, filter_params: ProductFilter) -> PaginatedResponse:
        query_filter = {}

        if filter_params.category:
            query_filter["category"] = filter_params.category
        if filter_params.brand:
            query_filter["brand"] = filter_params.brand
        if filter_params.min_price is not None:
            query_filter.setdefault("price", {})["$gte"] = filter_params.min_price
        if filter_params.max_price is not None:
            query_filter.setdefault("price", {})["$lte"] = filter_params.max_price
        if filter_params.size:
            query_filter["sizes.size"] = filter_params.size
        if filter_params.in_stock is not None:
            if filter_params.in_stock:
                query_filter["sizes"] = {"$elemMatch": {"stock": {"$gt": 0}}}
            else:
                query_filter["$or"] = [
                    {"sizes": {"$size": 0}},
                    {"sizes": {"$not": {"$elemMatch": {"stock": {"$gt": 0}}}}}
                ]
        if filter_params.search:
            query_filter["$or"] = [
                {"name": {"$regex": filter_params.search, "$options": "i"}},
                {"description": {"$regex": filter_params.search, "$options": "i"}},
                {"tags": {"$in": [filter_params.search]}}
            ]

        sort_options = [(filter_params.sort_by, -1 if filter_params.sort_order == "desc" else 1)] \
            if filter_params.sort_by else [("created_at", -1)]

        total_items = await self.collection.count_documents(query_filter)
        cursor = self.collection.find(query_filter).sort(sort_options).skip(pagination.skip).limit(pagination.limit)

        products = []
        async for product in cursor:
            product["id"] = str(product.pop("_id"))
            product["created_at"] = product["created_at"].isoformat()
            product["updated_at"] = product["updated_at"].isoformat() if product.get("updated_at") else None
            products.append(product)

        return PaginatedResponse.create(items=products, params=pagination, total_items=total_items)

    async def check_products_exist(self, product_ids: List[str]) -> Tuple[List[dict], List[str]]:
        """Check if products exist and return (found, missing)"""
        valid_object_ids = []
        for pid in product_ids:
            try:
                valid_object_ids.append(ObjectId(pid))
            except Exception:
                continue

        found_products_cursor = self.collection.find({"_id": {"$in": valid_object_ids}})
        found_products = await found_products_cursor.to_list(length=len(valid_object_ids))

        found_ids = {str(p["_id"]) for p in found_products}
        missing_ids = [pid for pid in product_ids if pid not in found_ids]

        return found_products, missing_ids
