from datetime import datetime, timedelta, timezone
import uuid
import time
from faker import Faker
fake = Faker('en_IN')
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, insert, func, text, asc
from threading import Thread

from .models import Customer
from src.account.schema import CreateCustomer
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from src.config import Config
import logging
import random

class CustomerService:
    BATCH_SIZE = 5000

    async def FetchAllCustomer(self, request, page, page_size, session):
        current_url = str(request.url)
        current_path = str(request.url).split("?")[0]
        query = text("""
                     select count(*) from customers
                     """)
        total_orders = await session.scalar(query)
        offset = (page - 1) * page_size
        stmt = select(Customer).order_by(asc("user_id")).limit(page_size).offset(offset)
        result = await session.execute(stmt)
        return {
            "total": total_orders,
            "current_url": current_url,
            "next_page": f"{current_path}?page={page + 1}&page_size={page_size}" ,
            "last_page": f"{current_path}?page={page - 1}&page_size={page_size}" if page > 1 else  current_url,
            "data": result.scalars().all()
        }
    

    async def CreateNewUser(self, session: AsyncSession):
        
        t1 = time.time()
        c=0
        total_customer = await session.scalar(select(func.count(Customer.user_id)))
        if total_customer < 10000:
            for batch_start in range(0, 100000, CustomerService.BATCH_SIZE):

                customers = []
                for i in range(batch_start, batch_start + CustomerService.BATCH_SIZE):
                    created_at = fake.date_time_between(
                        start_date="-2y",
                        end_date="now",
                        tzinfo=timezone.utc,
                    )
                    customers.append(
                        {
                            "customer_id": f"CUST{i:06d}",
                            "email": fake.unique.email(),
                            "full_name": fake.name(),
                            "contact_number": fake.unique.numerify(text="9#########"),
                            "full_address": fake.address(),
                            "state": fake.state(),
                            "pin_code": fake.postcode(),
                            "created_at": created_at,
                            "updated_at": created_at
                        }
                    )
                try:
                    await session.execute(insert(Customer), customers)
                    await session.commit()
                    print(f"Inserted {batch_start + len(customers)} customers")
                except Exception as e:
                    await session.rollback()
                    raise HTTPException(
                        detail=f"error: {str(e)}",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                finally:
                    pass
            t4= time.time() - t1
            print(f"total time taken in all data store: {t4:.2f} seconds")
            return JSONResponse(
                content={
                    'detail': "All customer data successfully starage.",
                    "time_taken_for cust_creation": f"{t4:.2f} seconds"
                    },
                status_code=status.HTTP_201_CREATED
            )
        return JSONResponse(
            content="customer record already exist.",
            status_code=status.HTTP_403_FORBIDDEN
        )     
                    
