from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum


class AdminBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    address: str
    country: str
    phone_number: int
    date_of_birth: date


class AssignTaskEnum(Enum):
    assign = "assign"
    unassign = "unassigned"


class AdminCreate(AdminBase):
    password: str


class User(AdminBase):
    id: int
    verified: bool
    is_active: bool

    class Config:
        orm_mode = True
