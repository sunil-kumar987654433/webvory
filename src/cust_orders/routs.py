from fastapi import APIRouter, Depends, HTTPException, status, Query, Request

from src.db.main import get_session
from .services import OrderService
from .schema import BussiessTrends, OrderResponse, SpendingByCustomer
from sqlalchemy.ext.asyncio import AsyncSession
order_router = APIRouter()
order_service = OrderService()

import uuid

@order_router.post("/generate-order")
async def generate_order( session: AsyncSession = Depends(get_session)):
    return await order_service.CreateOrder(session)

@order_router.get("/cancel-order")
async def cancel_order( session: AsyncSession = Depends(get_session)):
    return await order_service.CancelOrderGenerateRefund(session)

@order_router.get("/view-cancel-order")
async def fetch_all_cancel_order(
    request: Request,
    page: int = Query(ge=1, default=1),
    page_size: int = Query(ge=1, default=100),
    session: AsyncSession = Depends(get_session)):
    """
        you can view here refunded order
    """
    return await order_service.FetchAllCancelOrdersDetail(request, page, page_size, session)


@order_router.get("/view-all-order")
async def fetch_all_order(
    request: Request,
    page: int = Query(ge=1, default=1),
    page_size: int = Query(ge=1, default=100),
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch here all order
    """
    return await order_service.FetchAllOrders(request, page, page_size, session)

@order_router.get("/view-total-number-of-order")
async def fetch_total_number_of_order(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch total numbers order
    """
    return await order_service.FetchTotalOrders(request, session)


@order_router.get("/view-total-revenue")
async def fetch_total_revenue(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch total revenue
    """
    return await order_service.FetchTotalOrdersRevenue(request, session)

@order_router.get("/view-net-revenue")
async def fetch_total_revenue(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch net revenue
        net_revenue = amount_order - refund
    """
    return await order_service.FetchNetOrdersRevenue(request, session)

@order_router.get("/view-total-refund")
async def fetch_total_refund(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch total refund after cancled order
        
    """
    return await order_service.FetchTotalOrdersRefund(request, session)


@order_router.get("/average-order-amount")
async def average_order_amount(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch average order amount
        
    """
    return await order_service.FetchAverageOrdersAmount(request, session)


@order_router.get("/repeated-customer-revenue")
async def repeated_customer_revenue(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch average order amount
        
    """
    return await order_service.RepeatedCusRevenue(request, session)


@order_router.get("/revenue-trends")
async def revenue_trends(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    trends: BussiessTrends
    """
        you can fetch revenue according to year, month, day
        
    """
    return await order_service.BussinessRevenueTrends(trends, request, session)


@order_router.get("/top-customer-spending")
async def top_customer_spending(
    request: Request,
    spending_type: SpendingByCustomer,
    page: int = Query(ge=1, default=1),
    page_size: int = Query(ge=1, default=100),
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch here all order
    """
    return await order_service.PurchaseOrdersSpends(request, spending_type, page, page_size, session)
