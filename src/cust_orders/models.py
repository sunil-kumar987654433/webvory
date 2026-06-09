from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, DateTime, Boolean, Enum as SqlEnum, UUID, ForeignKey, DECIMAL
from src.db.db import Base
import uuid
from decimal import Decimal
from datetime import datetime, date, timezone
from enum import Enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from account.models import Customer

class OrderStatus(str, Enum):
    pending = 'pending'
    success = 'success'
    failed="failed"
    refunded="refunded"

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    order_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    customer_uid: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.user_key",ondelete="cascade"), nullable=False, index=True)
    payment_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal('0.00'))
    refund_amount: Mapped[Decimal] = mapped_column(DECIMAL(10,2), default=Decimal('0.00'))
    status: Mapped[OrderStatus] = mapped_column(SqlEnum(OrderStatus), default=OrderStatus.pending, index=True)
    refunded_at: Mapped[datetime | None] = mapped_column( DateTime(timezone=True))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc))
    customer : Mapped['Customer'] = relationship(back_populates='orders')

    def __repr__(self):
        return f"<Order (id: {self.order_id})>"
