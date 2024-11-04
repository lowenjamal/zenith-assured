from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum


class UserTypeEnum(str, Enum):
    customer = 'customer'
    admin = 'admin'
    super_admin = 'super_admin'


class UserLogin(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    address: str
    country: str
    phone_number: str
    date_of_birth: date


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    verified: bool
    is_active: bool

    class Config:
        orm_mode = True
