from pydantic import BaseModel, EmailStr, Field, ConfigDict
import uuid
from datetime import datetime


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


class CustomerResponse(BaseCustomer):
    user_id: int
    user_key: uuid.UUID
    user_type: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    hashed_password: str = Field(exclude=True)

    model_config = ConfigDict(
        from_attributes=True
    )
