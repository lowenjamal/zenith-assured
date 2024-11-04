from sqlalchemy import Boolean, Column, Date, Integer, String, DateTime, Enum, BigInteger
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime
from sqlalchemy.orm import relationship


from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    password = Column(String(255))
    address = Column(String(255))
    country = Column(String(255))
    phone_number = Column(BigInteger)
    date_of_birth = Column(Date)
    verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    id_verified = Column(Enum('unverified', 'verifying', 'verified', name='is_id_verified_enum'), default='unverified')
    user_type = Column(Enum('customer', 'admin', 'super_admin', name='user_type_enum'))
    can_auto_trade = Column(Boolean, default=False)
    auto_trade_count = Column(Integer, default=0)
    assigned_to = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())

    account = relationship("Account", uselist=False, back_populates="user")
    transactions = relationship("Transaction", uselist=False, back_populates="user")
    trading = relationship("TradeTable", back_populates="user")
    document_verifications = relationship("DocumentVerification", back_populates="user")

