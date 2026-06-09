from fastapi import APIRouter, Depends, HTTPException, status

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

@account_router.post("/generate-order")
async def generate_cust_order(session: AsyncSession = Depends(get_session)):
    return await customer_service.CreateNewCustomerOrder(session)