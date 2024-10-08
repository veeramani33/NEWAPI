from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.models import UserCoView, Users
from app.auth.schema import TokenData, UserInDB
from app.database import get_db

# TODO: Move to config
SECRET_KEY = "ffea719441cdc722c8f0d0f54beb36d0eac810ae15a72387399108da0a397c1f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password, db: Session):
    hashed_pwd = db.query(func.f.encode(password)).scalar()
    return hashed_pwd


def verify_password(plain_password: str, hashed_password: int, db: Session):
    new_hash_pwd = get_password_hash(plain_password, db)
    return new_hash_pwd == hashed_password


def get_user(login: str, db: Session):
    user = db.query(Users).filter(func.lower(Users.login) == login.lower()).first()
    return user 

def is_password_null(login: str, db: Session) -> bool:
    user = db.query(Users).filter(func.lower(Users.login) == login.lower()).filter(Users.password.is_(None)).first()
    return user is not None

def is_co_assigned(login: str, db: Session) -> bool:
    # Query for the user and co_code
    # print('co view check 1')
    user = db.query(UserCoView).filter(func.lower(UserCoView.login) == login.lower()).first()

    # Return True if the record exists, False otherwise
    return user is not None

def authenticate_user(login: str, password: str, password_update: bool, db: Session):

    
    """Authenticate a user by login and password.

    Args:
        login (str): The user's login (username or email).
        password (str): The user's password.
        db (Session): Database session.

    Returns:
        dict: A dictionary containing the user object and a message or new_user flag.   

    Raises:
        HTTPException: If the password is incorrect.
    """

    # Remove trailing spaces in login
    login = login.strip()

    user = get_user(login, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User doesn't exist")
    
    if password_update: 
        enctrypted_password = get_password_hash(password, db)
        print(enctrypted_password)

        # update the database 
        user.password = enctrypted_password
        db.commit()
 
    # Case 1: User exists but password is empty
    if user and password == "" and is_password_null(login, db) == False:
        return {"message": "Enter the password", "user": user}
    
    if user and password == "" and is_password_null(login, db) == True:
        if not is_co_assigned(login, db):
            return {"message": "there is no program created under this log in.", "user": user} 
        else:
            return {"user": user, "new_user": False}
    
    if user and password != "" and is_password_null(login, db) == True:
        return {"confirm_password": "Confirm password", "user": user}
 
    #case2: 
    if user and is_password_null(login, db):
        return {"user": user, "new_user": False}

    # If a password is provided, verify it
    if password or password == "":
        # print("hi4")
        if not user:
        
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not verify_password(password, user.password, db):
        
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials. Please check your password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    #We are checking whether user has program created or not. 
    #print(user)
    if user.grade!=0 and not is_co_assigned(login, db):
        print('co view check.')
        return {"message": "there is no program created under this log in.", "user": user} 

    if user is not None:
    # If authentication succeeds and a valid password is provided, return the user and indicate they are not new
        return {"user": user, "new_user": False}
    else:
        return {"message": "user doesn't exist", "user": ""}
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth_2_scheme), db: Session = Depends(get_db)
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        co_code: str = payload.get("co_code")

        if login is None:
            raise credential_exception

        token_data = TokenData(func.lower(Users.login) == login.lower(), co_code=co_code)

    except JWTError:
        raise credential_exception

    user = get_user(login, db)

    if user is None:
        raise credential_exception

    return token_data
