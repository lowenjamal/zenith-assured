from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class TransactionTypeEnum(Enum):
    deposit = "deposit"
    withdraw = "withdraw"


class BalanceType(str, Enum):
    main_balance = "main_balance"
    referral_balance = "referral_balance"
    bonus_balance = "bonus_balance"


class StatusTypeEnum(str, Enum):
    pending = 'pending'
    processing = 'processing'
    approved = 'approved'


class TransactionMethodEnum(str, Enum):
    card_payment = "card-payment"
    bank_transfer = "bank-transfer"
    cryptocurrency = "cryptocurrency"


class TransactionBase(BaseModel):
    user_id: int
    transaction_amount: int
    created_at: datetime


class TransactionCreate(TransactionBase):
    transaction_type: TransactionTypeEnum
    status: StatusTypeEnum = StatusTypeEnum.pending
    transaction_method: TransactionMethodEnum


class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode = True
