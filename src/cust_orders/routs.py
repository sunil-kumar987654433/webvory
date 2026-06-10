import json
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.redis import redis_client
from src.db.main import get_session
from .services import OrderService
from .schema import BussiessTrends1, BussiessTrends2, OrderResponse, SpendingByCustomer

order_router = APIRouter()
order_service = OrderService()


@order_router.post("/generate-order")
async def generate_order( session: AsyncSession = Depends(get_session)):
    """
        Create/Generate new all order
    """
    return await order_service.CreateOrder(session)

@order_router.get("/cancel-order")
async def cancel_order( session: AsyncSession = Depends(get_session)):
    """
    cancel 200000 order
    """
    return await order_service.CancelOrderGenerateRefund(session)           

@order_router.get("/view-cancel-order")
async def fetch_all_cancel_order(
    request: Request,
    page: int = Query(ge=1, default=1),
    page_size: int = Query(ge=1, default=100),
    session: AsyncSession = Depends(get_session)):
    """
        you can view here refunded order detail,
        redis cache expired in 60 second
    """
    cache_key = f"analytics:cancel_order:{page}:{page_size}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result =  await order_service.FetchAllCancelOrdersDetail(request, page, page_size, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result
    
    


@order_router.get("/view-all-order")
async def fetch_all_order(
    request: Request,
    page: int = Query(ge=1, default=1),
    page_size: int = Query(ge=1, default=100),
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch here all order,
        redis cache used and redis key, data expired in 60 seconds
    """
    cache_key = f"analytics:fetch_all_order:{page}:{page_size}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    result =  await order_service.FetchAllOrders(request, page, page_size, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result


@order_router.get("/view-total-number-of-order")
async def fetch_total_number_of_order(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch total numbers order,
        redis cache used and redis key, data expired in 60 seconds
    """
    cache_key = f"analytics:fetch_total_number_of_order"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    result =  await order_service.FetchTotalOrders(request, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result


@order_router.get("/view-total-revenue")
async def view_total_revenue(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch total revenue
        redis cache used and redis key, data expired in 60 seconds
    """
    cache_key = f"analytics:view_total_revenue"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    result =  await order_service.FetchTotalOrdersRevenue(request, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result

@order_router.get("/view-net-revenue")
async def fetch_net_revenue(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch net revenue
        net_revenue = amount_order - refund,
        redis based cache
    """
    cache_key = f"analytics:fetch_net_revenue"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result =  await order_service.FetchNetOrdersRevenue(request, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result

@order_router.get("/view-total-refund")
async def fetch_total_refund(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch total refund after cancled order,
        redis cache used , cache expired after 60 seconds    
    """
    cache_key = f"analytics:fetch_total_refund"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result =  await order_service.FetchTotalOrdersRefund(request, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result


@order_router.get("/average-order-amount")
async def average_order_amount(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch average order amount
        
    """
    cache_key = f"analytics:average_order_amount"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result =  await order_service.FetchAverageOrdersAmount(request, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result


@order_router.get("/repeated-customer-revenue")
async def repeated_customer_revenue(
    request: Request,
    session: AsyncSession = Depends(get_session)):
    """
        you can fetch average order amount
        
    """
    cache_key = f"analytics:repeated_customer_revenue"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result = await order_service.RepeatedCusRevenue(request, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result

    

@order_router.get("/revenue-trends")
async def revenue_trends( request: Request, trends1: BussiessTrends1, trends2: BussiessTrends2, session: AsyncSession = Depends(get_session)):
    """
        you can fetch revenue according to year, month, day
        
    """

    cache_key = f"analytics:revenue_trends:{trends1}:{trends2}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    result =  await order_service.BussinessRevenueTrends(trends1, trends2, request, session)
    
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result


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
    cache_key = f"analytics:top_customer_spending:{page}:{page_size}:{spending_type}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    result =  await order_service.PurchaseOrdersSpends(request, spending_type, page, page_size, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result