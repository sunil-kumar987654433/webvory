import uuid
import time
import logging
import secrets, random
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from faker import Faker
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from src.cust_orders.schema import BussiessTrends1, BussiessTrends2, SpendingByCustomer

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, insert, func, update, bindparam, text, asc
from threading import Thread
from src.account.models import Customer
from .models import Order, OrderStatus

from src.config import Config

fake = Faker('en_IN')


class OrderService:
    BATCH_SIZE = 5000

    async def is_check_order_exist(self, session: AsyncSession):
        total_order = await session.scalar(
            select(func.count(Order.order_id))
        )
        if total_order == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No orders found.",
            )
        return total_order
    

    async def PurchaseOrdersSpends(self, request: Request, spending_type: SpendingByCustomer, page: int, page_size: int, session: AsyncSession):
        await self.is_check_order_exist(session)
        order = "desc" if spending_type == SpendingByCustomer.desc else "asc"
        query = text(
            f"""
        select sum(o.amount) as max_purchasing, c.email, c.full_name , c.contact_number from orders o join customers c on o.customer_uid=c.user_key group by c.email, c.contact_number, c.full_name order by max_purchasing {order} LIMIT :limit OFFSET :offset;
        """
        )
        offset = (page - 1) * page_size
        
        result = await session.execute(query, {'limit': page_size, 'offset': offset})
        current_url = str(request.url)
        current_path = str(request.url).split("?")[0]
        

        return {
            
            "current_url": current_url,
            "next_page": f"{current_path}?spending_type={order}&page={page + 1}&page_size={page_size}" ,
            "last_page": f"{current_path}?spending_type={order}&page={page - 1}&page_size={page_size}" if page > 1 else  current_url,
            "data": result.mappings().all()
        }


    async def BussinessRevenueTrends(self, trends1: BussiessTrends1, trends2: BussiessTrends2, request, session):
        await self.is_check_order_exist(session)

        odr1 = 'year' if trends1 == 'year' else 'month'
        odr2 = 'month' if trends2 == 'month' else None

        if odr1 == 'year' and odr2 == 'month':
            query  = text("""
                          select sum(amount) as total_amount, EXTRACT(YEAR FROM created_at) as year, TO_CHAR(created_at, 'FMMonth') AS month_name, EXTRACT(MONTH FROM created_at) as month_no from orders group by EXTRACT(MONTH FROM created_at), EXTRACT(YEAR FROM created_at), TO_CHAR(created_at, 'FMMonth') order by  EXTRACT(MONTH FROM created_at) asc;
                           """)
            
        elif odr1 == 'month' and odr2 is None:
            query  = text("""
                select sum(o.amount) as total_amount, EXTRACT(MONTH FROM created_at) as month_no, TO_CHAR(created_at, 'FMMonth') AS month_name 
                          from orders o group by EXTRACT(MONTH FROM created_at), TO_CHAR(created_at, 'FMMonth') order by  EXTRACT(MONTH FROM created_at) asc;
            """)
        
        
        
        elif odr1 == 'year' and odr2 is None:
            query  = text("""
            select sum(amount) as total_amount, EXTRACT(YEAR FROM created_at) as year from orders 
                          group by EXTRACT(YEAR FROM created_at) order by  EXTRACT(YEAR FROM created_at) asc;
            """)
        result = await session.execute(query)
        return result.mappings().all()



    async def RepeatedCusRevenue(self, request, session):
        query = text("""
            select COALESCE(sum(user_total_purchasing), 0.00), COALESCE(sum(total_repeated_cust), 0)  from (select sum(amount) as user_total_purchasing, customer_uid, count(customer_uid) as total_repeated_cust, count(order_id) from orders group by customer_uid having count(order_id) > 1) as subquery
                     """)
        await self.is_check_order_exist(session)
        result = await session.execute(query)
        revenue, total_repeated_cust = result.one()
        
        print(revenue, total_repeated_cust)
        return JSONResponse(
            content= {
                "Repeated_Revenue": round(revenue.quantize(Decimal("0.01"))),
                "Repeated_customer": int(total_repeated_cust)
            },
            status_code=status.HTTP_200_OK
        )


    async def FetchAverageOrdersAmount(self, request, session):
        await self.is_check_order_exist(session)

        result =  (await session.scalar(select(func.avg(Order.amount)))) or Decimal('0.00')
        return result.quantize(Decimal("0.01"))
    
    async def FetchTotalOrdersRefund(self, request, session):
        await self.is_check_order_exist(session)
        result =  (await session.scalar(select(func.sum(Order.amount)).where(Order.status == OrderStatus.refunded))) or Decimal('0.00')
        return result.quantize(Decimal("0.01"))
    async def FetchNetOrdersRevenue(self, request, session):
        await self.is_check_order_exist(session)
        result =  (await session.scalar(select(func.sum(Order.amount- Order.refund_amount)))) or Decimal('0.00')
        return result.quantize(Decimal("0.01"))

    async def FetchTotalOrdersRevenue(self, request, session):
        await self.is_check_order_exist(session)
        result =  (await session.scalar(select(func.sum(Order.amount)))) or Decimal('0.00')
        return result.quantize(Decimal("0.01"))
    
    async def FetchTotalOrders(self, request, session):
        await self.is_check_order_exist(session)
        return (await session.scalar(select(func.count(Order.order_id)))) or 0
    
    async def FetchAllOrders(self, request, page, page_size, session):
        await self.is_check_order_exist(session)
        current_url = str(request.url)
        current_path = str(request.url).split("?")[0]
        query = text("""
                     select count(*) from orders
                     """)
        total_orders = await session.scalar(query)
        offset = (page - 1) * page_size
        stmt = select(Order).order_by(asc("order_id")).limit(page_size).offset(offset)
        result = await session.execute(stmt)
        return {
            "total": total_orders,
            "current_url": current_url,
            "next_page": f"{current_path}?page={page + 1}&page_size={page_size}" ,
            "last_page": f"{current_path}?page={page - 1}&page_size={page_size}" if page > 1 else  current_url,
            "data": result.scalars().all()
        }
    

    async def FetchAllCancelOrdersDetail(self,request: Request, page: int, page_size: int, session: AsyncSession):
        await self.is_check_order_exist(session)
        current_url = str(request.url)
        current_path = str(request.url).split("?")[0]
        query = text("""
                     select count(*) from orders where status= :status
                     """)
        total_cancel_orders = await session.scalar(query, {"status": 'refunded'})
        offset = (page - 1) * page_size
        # query1 = text("""
        #     select * from orders 
        #     LIMIT :page_size 
        #     OFFSET :offset 
        # """)
        # record = await session.execute(query1, {"page_size": page_size, 'offset': offset })
        # return record.fetchall()
        stmt = select(Order).where(Order.status == OrderStatus.refunded).order_by(asc("order_id")).limit(page_size).offset(offset)
        result = (await session.execute(stmt)) or None
        if result:
            return {
                "total": total_cancel_orders,
                "current_url": current_url,
                "next_page": f"{current_path}?page={page + 1}&page_size={page_size}" ,
                "last_page": f"{current_path}?page={page - 1}&page_size={page_size}" if page > 1 else  current_url,
                "data": result.scalars().all()
            }
        return JSONResponse(
            content="Till now no order exist that is cancled",
            status_code=status.HTTP_200_OK
        )
    
    
    async def CancelOrderGenerateRefund(
        self,
        session: AsyncSession,
    ):
        t1 = time.time()
        await self.is_check_order_exist(session)
        result = await session.execute(
            select(
                Order.order_id,
                Order.amount,
                Order.created_at,
            ).where(
                Order.status == OrderStatus.success
            )
        )

        all_orders = result.all()
        if len(all_orders) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No successful orders found.",
            )
        refund_count = min(200000, len(all_orders))
        selected_orders = random.sample(
            all_orders,
            refund_count,
        )
        for batch_start in range(
            0,
            refund_count,
            self.BATCH_SIZE,
        ):
            batch = selected_orders[
                batch_start:
                batch_start + self.BATCH_SIZE
            ]
            updates = []
            for order_id, amount, created_at in batch:
                refunded_at = created_at + timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )
                updates.append(
                    {
                        "order_id": order_id,
                        "refund_amount": amount,
                        "status": OrderStatus.refunded,
                        "refunded_at": refunded_at,
                        "updated_at": refunded_at,
                    }
                )
            try:
                await session.run_sync(
                    lambda sync_session: sync_session.bulk_update_mappings(
                        Order,
                        updates,
                    )
                )
                await session.commit()
                print(
                    f"Updated {batch_start + len(batch)} orders"
                )
            except Exception as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e),
                )
        total_time = time.time() - t1
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "detail": "Refund orders generated successfully.",
                "updated_orders": refund_count,
                "time_taken": f"{total_time:.2f} seconds",
            },
        )
            

    async def CreateOrder(self, session: AsyncSession):
        t1 = time.time()
        c=0
        total_order = await session.scalar(select(func.count(Order.order_id)))
        if total_order < 100:
            
            all_customers = await session.execute(select(Customer.user_key, Customer.created_at))
            
            customer_details = all_customers.all()
            if len(customer_details) == 0:
                raise HTTPException(
                    detail='Customer not exist',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            for batch_start in range(0, 1000000, OrderService.BATCH_SIZE):
                orders = []
                for i in range(batch_start, batch_start + OrderService.BATCH_SIZE):
                    customer_uid, cust_created_date = random.choice(customer_details)
                    order_created_at = cust_created_date + timedelta(
                        days=random.randint(0, 600),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    orders.append(
                        {
                            "payment_id": f"ODR{secrets.token_hex(16)}{i:06d}",
                            'customer_uid': customer_uid,
                            "amount": random.randint(1000, 10000),
                            "status": OrderStatus.success,
                            'created_at': order_created_at,
                            "updated_at": order_created_at
                        }
                    )
                try:
                    await session.execute(insert(Order), orders)
                    await session.commit()
                    print(f"Inserted {batch_start + len(orders)} orders")
                except Exception as e:
                    await session.rollback()
                    raise HTTPException(
                        detail=f"error: {str(e)}",
                        status_code=status.HTTP_403_FORBIDDEN
                    )
                finally:
                    pass
                    # print(f"total time consume for 5000 order created: {t3-t2:.2f} seconds", )

            t4 = time.time()-t1
            print(f"total time taken in all data store: {t4:.2f} seconds")
            return JSONResponse(
                content={'detail': "All order successfully starage.",
                            'time_taken_in_order_create': f"{t4:.2f} seconds"
                            },
                status_code=status.HTTP_201_CREATED
            )

        return JSONResponse(
            content="All Order record already exist.",
            status_code=status.HTTP_403_FORBIDDEN
        )       
