from pydantic import BaseModel
from enum import Enum


class CryptoCurrencyWalletCreate(BaseModel):
    wallet_address: str
    network_chain: str
    preferred_token: str

    class Config:
        orm_mode = True


class BankDetailsCreate(BaseModel):
    bank_name: str
    account_name: str
    iban: str
    bic: str
    reference: str

    class Config:
        orm_mode = True


# class TransactionType(Enum):
#     deposit = "deposit"
#     withdraw = "withdraw"


class CardDetailsCreate(BaseModel):
    firstname: str
    lastname: str
    card_number: int
    expiry_date: str
    cvv: int

    class Config:
        orm_mode = True


class CryptoCurrencyWithdrawCreate(BaseModel):
    wallet_address: str
    network_chain: str
    preferred_token: str

    class Config:
        orm_mode = True
