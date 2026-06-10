import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.schema import CreateCustomer, CustomerResponse
from src.db.main import get_session
from .services import CustomerService
from src.redis import redis_client


account_router = APIRouter()
customer_service = CustomerService()

@account_router.post("/generate-customer")
async def generate_customer( session: AsyncSession = Depends(get_session)):
    await redis_client.flushall()
    return await customer_service.CreateNewUser(session)


@account_router.get("/view-all-customers")
async def fetch_all_customer(
    request: Request,
    page: int = Query(ge=1, default=1),
    page_size: int = Query(ge=1, default=100),
    session: AsyncSession = Depends(get_session)):
    """
        you can view here order order,
        redis used here as cache data, cache expired in 60 seconds
    """

    cache_key = f"analytics:repeated_customer_revenue"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    result = await customer_service.FetchAllCustomer(request, page, page_size, session)
    await redis_client.set(
        cache_key,
        json.dumps(jsonable_encoder(result)),
        ex=60
    )
    return result