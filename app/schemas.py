from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import List, Optional


# -----------------------------
# 1. CUSTOMER SCHEMAS
# -----------------------------

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# 2. ORDER ITEM SCHEMAS
# -----------------------------

class OrderItemCreate(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=100)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


# -----------------------------
# 3. ORDER SCHEMAS
# -----------------------------

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]


class OrderConfirm(BaseModel):
    status: str = Field(..., pattern="^(CONFIRMED)$")


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


# -----------------------------
# 4. INVOICE SCHEMAS
# -----------------------------

class InvoiceCreate(BaseModel):
    order_id: int
    due_date: date
    discount_type: Optional[str] = Field(None, pattern="^(FLAT|PERCENT)$")
    discount_value: Optional[float] = Field(0, ge=0)


class InvoiceResponse(BaseModel):
    id: int
    order_id: int
    subtotal: float
    tax: float
    total: float
    due_date: date
    status: str
    discount_type: Optional[str]
    discount_value: float
    created_at: datetime

    class Config:
        from_attributes = True


# -----------------------------
# 5. PAYMENT SCHEMAS
# -----------------------------

class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(CASH|CARD|UPI|BANK_TRANSFER)$")


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_method: str
    paid_at: datetime

    class Config:
        from_attributes = True
