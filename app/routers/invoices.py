from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.database import get_db
from app.schemas import InvoiceResponse
from app.services.invoice_service import (
    create_invoice,
    get_invoice,
)

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


# -----------------------------
# CREATE INVOICE FOR AN ORDER
# -----------------------------
@router.post(
    "/orders/{order_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_for_order(
    order_id: int,
    discount_type: str | None = None,
    discount_value: Decimal = Decimal("0.00"),
    db: Session = Depends(get_db),
):
    try:
        invoice = create_invoice(
            db=db,
            order_id=order_id,
            discount_type=discount_type,
            discount_value=discount_value,
        )
        return invoice

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# -----------------------------
# GET INVOICE BY ID
# -----------------------------
@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice_by_id(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_invoice(db, invoice_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
