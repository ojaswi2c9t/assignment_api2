from bson import ObjectId
from fastapi import HTTPException
from typing import List, Dict


def convert_objectid(object_id: str) -> ObjectId:
    try:
        return ObjectId(object_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")


def calculate_total_amount(
    items: List[Dict], products: List[Dict]
) -> float:
    """Calculate total bill based on quantity and matched product sizes and prices"""

    product_map = {str(p["_id"]): p for p in products}
    total = 0.0

    for item in items:
        product_id = item["product_id"]
        size = item.get("size")
        quantity = item["quantity"]

        product = product_map.get(product_id)
        if not product:
            raise HTTPException(status_code=400, detail=f"Invalid product ID: {product_id}")

        # Look for the matching size
        size_info = next((s for s in product.get("sizes", []) if s["size"] == size), None)
        if not size_info:
            raise HTTPException(
                status_code=400,
                detail=f"Size '{size}' not available for product '{product['name']}'."
            )

        price = product["price"]
        total += price * quantity

    return round(total, 2)


class ValidationHelper:
    @staticmethod
    def validate_order_data(data: dict) -> dict:
        if "user_id" not in data or not data["user_id"]:
            raise HTTPException(status_code=400, detail="Missing user_id in order")
        if "items" not in data or not isinstance(data["items"], list) or not data["items"]:
            raise HTTPException(status_code=400, detail="Empty or invalid items in order")

        for item in data["items"]:
            if "product_id" not in item or "quantity" not in item or "size" not in item:
                raise HTTPException(status_code=400, detail="Each item must have product_id, quantity, and size")
        return data
