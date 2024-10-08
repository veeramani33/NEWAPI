from pydantic import BaseModel


class Output(BaseModel, str_strip_whitespace=True):
    sl_no: int
    code: str
    name: str

    class Config:
        from_attributes = True
