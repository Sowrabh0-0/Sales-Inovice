from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.invoice import Invoice
from app.models.payment import Payment

def refund_payment(
    db: Session,
    invoice_id: int,
    amount: Decimal,
    reason: str | None = None,
) -> Payment:
    amount = Decimal(str(amount))

    if amount <= Decimal("0.00"):
        raise ValueError("Refund amount must be greater than zero")

    # 1️⃣ Validate invoice
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise ValueError("Invoice not found")

    if invoice.status == "CANCELLED":
        raise ValueError("Cannot refund a cancelled invoice")

    # 2️⃣ Calculate total paid so far
    total_paid = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.invoice_id == invoice_id)
        .scalar()
    )
    total_paid = Decimal(str(total_paid))

    if total_paid <= Decimal("0.00"):
        raise ValueError("No payments found to refund")

    # 3️⃣ Prevent over-refund
    if amount > total_paid:
        raise ValueError("Refund amount exceeds paid amount")

    # 4️⃣ Create refund (negative payment)
    refund = Payment(
        invoice_id=invoice_id,
        amount=-amount,
        payment_method="REFUND",
        paid_at=datetime.now(timezone.utc),
        note=reason,
    )

    db.add(refund)
    db.flush()

    # 5️⃣ Recalculate invoice status
    new_total_paid = total_paid - amount

    if new_total_paid == Decimal("0.00"):
        invoice.status = "UNPAID"
    elif new_total_paid < invoice.total:
        invoice.status = "PARTIALLY_PAID"
    else:
        invoice.status = "PAID"

    db.commit()
    db.refresh(refund)

    return refund
