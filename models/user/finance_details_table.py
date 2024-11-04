from sqlalchemy import Column, Integer, String, Enum, DateTime, BigInteger
from database import Base
from datetime import datetime


class CryptoCurrencyWallet(Base):
    __tablename__ = "crypto_currency_wallet"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), unique=True, index=True)
    network_chain = Column(String(255))
    preferred_token = Column(String(255))


class BankDetails(Base):
    __tablename__ = "bank_details"

    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(255))
    account_name = Column(String(255))
    iban = Column(String(255))
    bic = Column(String(255))
    reference = Column(String(255))
    owner = Column(Enum('admin', 'user', name='owner_type_enum'))


class CardDetails(Base):
    __tablename__ = "card_details"

    id = Column(Integer, primary_key=True)
    firstname = Column(String(255))
    lastname = Column(String(255))
    card_number = Column(BigInteger)
    expiry_date = Column(String(255))
    cvv = Column(Integer)
    transaction_type = Column(Enum('deposit', 'withdraw', name='card_details_type'))
    created_at = Column(DateTime, default=datetime.now())


class CryptoCurrencyWithdraw(Base):
    __tablename__ = "crypto_currency_withdraw"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), unique=True, index=True)
    network_chain = Column(String(255))
    preferred_token = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())
