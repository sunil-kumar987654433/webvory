from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict
import uuid
from datetime import datetime
from decimal import Decimal

from src.account.schema import CustomerResponse

class BaseCustomer(BaseModel):
    customer_id: str
    email: EmailStr
    full_name: str  = Field(title="Full Name of User")
    contact_number: str = Field(title="mobile number of customer")
    full_address: str = Field(title="full address of customer")
    state: str = Field(title="state of customer")
    pin_code: str = Field(title="pin code of customer")

    

class CreateCustomer(BaseCustomer):
    pass

class BussiessTrends(str, Enum):
    year = 'year'
    day = 'day'
    month = 'month'

class SpendingByCustomer(str, Enum):
    desc = 'desc'
    asc = 'asc'



class OrderResponse(BaseCustomer):
    max_purchasing: Decimal
    customer: CustomerResponse

    model_config = ConfigDict(
        from_attributes=True
    )
