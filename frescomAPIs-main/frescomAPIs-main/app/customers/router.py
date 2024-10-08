from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.shared.models import Customer as CustomerModel

from .schema import Customers as CustomerSchema

# Define the router for customer-related endpoints
router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)


# Endpoint to retrieve a list of all customers
@router.get(
    "/",
    summary="Retrieve a list of all customers",
    response_description="A list of customer objects",
    status_code=status.HTTP_200_OK,
    response_model=List[CustomerSchema],
)
async def get_customers(db: Session = Depends(get_db)):
    """
    Retrieves a list of all customers from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[CustomerSchema]: A list of customer objects.
    """
    # Query the database for all customers
    customers_list = db.query(CustomerModel).all()

    # If no customers are found, raise a 404 error
    if not customers_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No customers found"
        )

    # Return the list of customers
    return customers_list
