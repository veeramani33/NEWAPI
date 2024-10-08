from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth import router as auth_router
from app.customers import router as customers_router
from app.database import get_db
from app.logger import logger
from app.middleware import log_middleware
from app.purchase_order import router as po_router
from app.shared import router as global_router

app = FastAPI()
logger.info("Starting API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    BaseHTTPMiddleware,
    dispatch=log_middleware,
)

app.include_router(auth_router.router)
app.include_router(global_router.router)
app.include_router(customers_router.router)
app.include_router(po_router.router)


@app.get("/")
def entry_point():
    return {"message": "Hello World"}


# ! TEST PASSWORD ENCODE FUNCTION. DO NOT USE IN PRODUCTION
# ? Experimental run of a procedure written in UTTARA database. A working example.
@app.get("/test")
def get_login_test(db: Session = Depends(get_db)):
    # Construct the PL/SQL statement
    encoded_pass = db.query(func.f.encode("mls")).scalar()

    return {"encoded password": encoded_pass}


add_pagination(app)
