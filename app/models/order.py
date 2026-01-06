from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, CheckConstraint
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="CREATED"
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="order", uselist=False)

    __table_args__ = (
        CheckConstraint(
            status.in_(["CREATED", "CONFIRMED"]),
            name="check_order_status"
        ),
    )
