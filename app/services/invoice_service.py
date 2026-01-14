from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.invoice import Invoice


TAX_RATE = Decimal("0.18")  # 18% tax


# -----------------------------
# CREATE INVOICE
# -----------------------------
def create_invoice(
    db: Session,
    order_id: int,
    discount_type: str | None = None,
    discount_value: Decimal = Decimal("0.00"),
) -> Invoice:
    # 1️⃣ Validate order
    order = db.get(Order, order_id)
    if not order:
        raise ValueError("Order not found")

    if order.status != "CONFIRMED":
        raise ValueError("Invoice can be created only for CONFIRMED orders")

    # 2️⃣ Ensure one invoice per order
    existing_invoice = (
        db.query(Invoice)
        .filter(Invoice.order_id == order_id)
        .first()
    )
    if existing_invoice:
        raise ValueError("Invoice already exists for this order")

    # 3️⃣ Fetch order items
    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id)
        .all()
    )

    if not items:
        raise ValueError("Order has no items")

    # 4️⃣ Calculate subtotal
    subtotal = sum(
        Decimal(item.quantity) * Decimal(item.unit_price)
        for item in items
    )

    # 5️⃣ Calculate tax
    tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))

    # 6️⃣ Apply discount
    discount_amount = Decimal("0.00")

    if discount_type == "FLAT":
        discount_amount = discount_value

    elif discount_type == "PERCENT":
        discount_amount = (subtotal * discount_value / Decimal("100")).quantize(
            Decimal("0.01")
        )

    # Prevent negative totals
    if discount_amount > subtotal:
        raise ValueError("Discount cannot exceed subtotal")

    # 7️⃣ Final total
    total = (subtotal + tax - discount_amount).quantize(Decimal("0.01"))

    # 8️⃣ Create invoice
    invoice = Invoice(
        order_id=order_id,
        subtotal=subtotal,
        tax=tax,
        total=total,
        discount_type=discount_type,
        discount_value=discount_value,
        status="UNPAID",
        due_date=(datetime.now(timezone.utc) + timedelta(days=30)).date(),
        created_at=datetime.now(timezone.utc),
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


# -----------------------------
# GET INVOICE
# -----------------------------
def get_invoice(db: Session, invoice_id: int) -> Invoice:
    invoice = db.get(Invoice, invoice_id)

    if not invoice:
        raise ValueError("Invoice not found")

    return invoice
