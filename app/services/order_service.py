from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem


# -----------------------------
# CREATE CUSTOMER
# -----------------------------
def create_customer(db: Session, name: str, email: str) -> Customer:
    customer = Customer(
        name=name,
        email=email,
        created_at=datetime.now(timezone.utc),
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


# -----------------------------
# CREATE ORDER WITH ITEMS
# -----------------------------
def create_order(db: Session, customer_id: int, items: list) -> Order:
    # validate customer
    customer = db.get(Customer, customer_id)
    if not customer:
        raise ValueError("Customer not found")

    order = Order(
        customer_id=customer_id,
        status="CREATED",
        created_at=datetime.now(timezone.utc),
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # add order items
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_name=item["product_name"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)

    return order


# -----------------------------
# CONFIRM ORDER
# -----------------------------
def confirm_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)

    if not order:
        raise ValueError("Order not found")

    if order.status != "CREATED":
        raise ValueError("Only CREATED orders can be confirmed")

    order.status = "CONFIRMED"
    db.commit()
    db.refresh(order)

    return order


# -----------------------------
# GET ORDER
# -----------------------------
def get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)

    if not order:
        raise ValueError("Order not found")

    return order
