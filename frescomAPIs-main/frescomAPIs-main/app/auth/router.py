from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schema import Token,LoginRequest
from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Auth route"],
)

     
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: LoginRequest,  # Replacing OAuth2PasswordRequestForm
    db: Session = Depends(get_db),
):
    user_response = service.authenticate_user(form_data.username, form_data.password, form_data.password_update, db)

    if "message" in user_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=user_response["message"],
        )
    
    if "confirm_password" in user_response:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=user_response["confirm_password"],
        )
    
    # if "no_prog_code" in user_response:
    #     raise HTTPException(
    #         status_code=status.HTTP_204_NO_CONTENT,
    #         detail=user_response["no_prog_code"],
    #     )

    user = user_response["user"]
    new_user = user_response["new_user"]

    # If the user is new, return a response indicating that
    if new_user:
        return {"new_user": True}

    # Continue with token generation for authenticated users
    access_token_expires = timedelta(minutes=service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": user.login, "co_code": user.co_code},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer", "new_user": False}