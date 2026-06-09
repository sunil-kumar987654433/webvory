from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, DateTime, Boolean, Enum as SqlEnum, UUID
from src.db.db import Base
import uuid
from datetime import datetime, date, timezone
from enum import Enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cust_orders.models import Order

class Customer(Base):
    __tablename__ = "customers"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(String(500), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    full_name: Mapped[str] = mapped_column(String(100))
    contact_number: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    full_address: Mapped[str] = mapped_column(String(300), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    pin_code: Mapped[str] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc))

    orders: Mapped[list['Order']] = relationship(back_populates='customer', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Customer (id: {self.user_id})>"
