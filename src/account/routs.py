from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.account.schema import CreateCustomer, CustomerResponse
from src.db.main import get_session
from .services import CustomerService
from sqlalchemy.ext.asyncio import AsyncSession
account_router = APIRouter()
customer_service = CustomerService()

import uuid

@account_router.post("/generate-customer")
async def generate_customer( session: AsyncSession = Depends(get_session)):
    return await customer_service.CreateNewUser(session)


@account_router.get("/view-all-customers")
async def fetch_all_customer(
    request: Request,
    page: int = Query(ge=1, default=1),
    page_size: int = Query(ge=1, default=100),
    session: AsyncSession = Depends(get_session)):
    """
        you can view here order order
    """
    return await customer_service.FetchAllCustomer(request, page, page_size, session)