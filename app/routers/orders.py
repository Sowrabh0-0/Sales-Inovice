from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CustomerCreate,
    CustomerResponse,
    OrderCreate,
    OrderResponse,
)
from app.services.order_service import (
    create_customer as create_customer_service,
    create_order as create_order_service,
    confirm_order as confirm_order_service,
    get_order as get_order_service,
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)



@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
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

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_order_service(
            db=db,
            customer_id=data.customer_id,
            items=[item.dict() for item in data.items],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@router.post(
    "/{order_id}/confirm",
    response_model=OrderResponse,
)
def confirm_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        return confirm_order_service(
            db=db,
            order_id=order_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_order_service(
            db=db,
            order_id=order_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
