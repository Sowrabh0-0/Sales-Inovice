from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem

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


# -----------------------------
# UPDATE ORDER ITEMS
# -----------------------------
def update_order_items(
    db: Session,
    order_id: int,
    items: list,
) -> Order:
    order = db.get(Order, order_id)

    if not order:
        raise ValueError("Order not found")

    if order.status != "CREATED":
        raise ValueError("Only CREATED orders can be updated")

    try:
        # 1. Delete existing items
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()

        # 2. Insert new items
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

    except SQLAlchemyError:
        db.rollback()
        raise

# -----------------------------
# CANCEL ORDER
# -----------------------------
def cancel_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)

    if not order:
        raise ValueError("Order not found")

    if order.status == "CONFIRMED":
        raise ValueError("Confirmed orders cannot be cancelled")

    if order.status == "CANCELLED":
        raise ValueError("Order already cancelled")

    if order.status != "CREATED":
        raise ValueError("Only CREATED orders can be cancelled")

    order.status = "CANCELLED"
    db.commit()
    db.refresh(order)

    return order
