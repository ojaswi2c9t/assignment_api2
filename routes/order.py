from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from typing import Optional
from bson import ObjectId

from core.database import get_database
from schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderOut,
    OrderFilter,
    OrderPaginatedResponse,
)
from schemas.common import MessageResponse
from schemas.pagination import PaginationParams
from services.order_service import OrderService
from models.order import OrderStatus, PaymentStatus

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db=Depends(get_database)
):
    order_service = OrderService(db)
    try:
        return await order_service.create_order(order.dict())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=OrderPaginatedResponse)
async def list_orders(
    pagination: PaginationParams = Depends(),
    user_id: Optional[str] = None,
    order_status: Optional[OrderStatus] = None,
    payment_status: Optional[PaymentStatus] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db=Depends(get_database)
):
    order_service = OrderService(db)
    filter_params = OrderFilter(
        user_id=user_id,
        order_status=order_status,
        payment_status=payment_status,
        min_total=min_total,
        max_total=max_total,
        date_from=date_from,
        date_to=date_to
    )
    return await order_service.list_orders(pagination, filter_params)

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: str = Path(..., title="The ID of the order to get"),
    db=Depends(get_database)
):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    order_service = OrderService(db)
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.patch("/{order_id}", response_model=OrderOut)
async def update_order_status(
    order_update: OrderUpdate,
    order_id: str = Path(..., title="The ID of the order to update"),
    db=Depends(get_database)
):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    order_service = OrderService(db)
    success = await order_service.update_order_status(order_id, order_update.status)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return await order_service.get_order_by_id(order_id)

@router.delete("/{order_id}", response_model=MessageResponse)
async def cancel_order(
    order_id: str = Path(..., title="The ID of the order to cancel"),
    db=Depends(get_database)
):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )
    order_service = OrderService(db)
    cancelled = await order_service.delete_order(order_id)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or already cancelled"
        )
    return MessageResponse(message=f"Order {order_id} cancelled successfully")
