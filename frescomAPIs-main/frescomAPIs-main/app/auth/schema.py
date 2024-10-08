from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    login: str | None = None
    co_code: str | None = None


class User(BaseModel):
    login: str | None = None
    co_code: str | None = None


class UserInDB(User):
    password: int

class LoginRequest(BaseModel):
    username: str
    password: str = None  # Optional field
    password_update: bool = None