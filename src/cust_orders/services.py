from datetime import datetime, timedelta, timezone
import uuid
import time
from faker import Faker
fake = Faker('en_IN')
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, insert, func
from threading import Thread

from .models import Customer
from src.account.schema import CreateCustomer
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from src.config import Config
import logging

class CustomerService:
    BATCH_SIZE = 5000
    

            

    async def CreateNewUser(self, session: AsyncSession):
        t1 = time.time()
        c=0
        total_customer = await session.scalar(select(func.count(Customer.user_id)))
        if total_customer == 0:
            for batch_start in range(0, 100000, CustomerService.BATCH_SIZE):
                t2 = time.time()

                customers = []
                for i in range(batch_start, batch_start + CustomerService.BATCH_SIZE):
                    customers.append(
                        {
                            "customer_id": f"CUST{i:06d}",
                            "email": fake.unique.email(),
                            "full_name": fake.name(),
                            "contact_number": fake.unique.numerify(text="9#########"),
                            "full_address": fake.address(),
                            "state": fake.state(),
                            "pin_code": fake.postcode(),
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
                    t3 = time.time()
                    c += 1
                    # print(f"total time consumes after each 5000 data store: {t3-t2:.2f} seconds", )
                    if c==20:
                        print(f"total time taken in all data store: {time.time()-t1:.2f} seconds")
                        return JSONResponse(
                            content="All customer data successfully starage.",
                            status_code=status.HTTP_201_CREATED
                        )
                    

    async def CreateNewCustomerOrder(self, session: AsyncSession):
        pass
        # t1 = time.time()
        # c=0
        # total_customer_order = await session.scalar(select(func.count(Order.order_id)))
        # if total_customer_order == 0:
        #     for batch_start in range(0, 100000, CustomerService.BATCH_SIZE):
        #         t2 = time.time()

        #         customers = []
        #         for i in range(batch_start, batch_start + CustomerService.BATCH_SIZE):
        #             customers.append(
        #                 {
        #                     "customer_id": f"CUST{i:06d}",
        #                     "email": fake.unique.email(),
        #                     "full_name": fake.name(),
        #                     "contact_number": fake.unique.numerify(text="9#########"),
        #                     "full_address": fake.address(),
        #                     "state": fake.state(),
        #                     "pin_code": fake.postcode(),
        #                 }
        #             )
        #         try:
        #             await session.execute(insert(Customer), customers)
        #             await session.commit()
        #             print(f"Inserted {batch_start + len(customers)} customers")
        #         except Exception as e:
        #             await session.rollback()
        #             raise HTTPException(
        #                 detail=f"error: {str(e)}",
        #                 status_code=status.HTTP_403_FORBIDDEN
        #             )
        #         finally:
        #             t3 = time.time()
        #             c += 1
        #             # print(f"total time consumes after each 5000 data store: {t3-t2:.2f} seconds", )
        #             if c==20:
        #                 print(f"total time taken in all data store: {time.time()-t1:.2f} seconds")
        #                 return JSONResponse(
        #                     content="All customer data successfully starage.",
        #                     status_code=status.HTTP_201_CREATED
        #                 )
