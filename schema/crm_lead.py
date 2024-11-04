from pydantic import BaseModel
from datetime import date
from enum import Enum


class StatusEnum(str, Enum):
    Not_Called = "Not Called"
    Unavailable = "Unavailable"
    Call_Back = "Call back"
    Not_Interested = "Not Interested"


class CRMUserBaseSchema(BaseModel):
    email: str
    first_name: str
    last_name: str
    address: str
    country: str
    phone_number: int
    date_of_birth: date
    status: StatusEnum
    activated: bool

    class Config:
        orm_mode = True
