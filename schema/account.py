from pydantic import BaseModel
from enum import Enum


class AccountTypeEnum(str, Enum):
    basic = 'basic'
    premium = 'premium'
    gold = 'gold'
    platinum = 'platinum'


class AccountBase(BaseModel):
    user_id: int
    account_type: AccountTypeEnum
    main_balance: int
    referral_balance: int
    bonus_balance: int


class AccountCreate(AccountBase):
    pass


class Account(AccountBase):
    id: int

    class Config:
        orm_mode = True
