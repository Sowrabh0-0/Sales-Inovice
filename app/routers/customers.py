from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import (
    create_customer_service,
    get_customer,
    list_customers,
    update_customer,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)

@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_api(
    data: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_customer_service(
            db=db,
            name=data.name,
            email=data.email,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_api(customer_id: int, db: Session = Depends(get_db)):
    try:
        return get_customer(db, customer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=list[CustomerResponse])
def list_customers_api(db: Session = Depends(get_db)):
    return list_customers(db)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer_api(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_customer(
            db=db,
            customer_id=customer_id,
            name=payload.name,
            email=payload.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
