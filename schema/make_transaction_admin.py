from pydantic import BaseModel, constr
from enum import Enum


class TransactionType(str, Enum):
    deposit = "deposit"
    withdraw = "withdraw"


class BalanceType(str, Enum):
    main_balance = "main_balance"
    referral_balance = "referral_balance"
    bonus_balance = "bonus_balance"


class MakeTransaction(BaseModel):
    user_id: int
    amount: int
    balance_type: BalanceType
    transaction_type: TransactionType

    class Config:
        use_enum_values = True


class IdVerificationEnum(str, Enum):
    unverified = "unverified"
    verifying = "verifying"
    verified = "verified"
