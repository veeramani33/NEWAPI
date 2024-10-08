from pydantic import BaseModel


class Customers(BaseModel):
    code: str
    name: str
