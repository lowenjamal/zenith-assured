from sqlalchemy import Column, Enum, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from database import Base


class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    account_type = Column(Enum('basic', 'premium', 'gold', 'platinum', name='account_type_enum'))
    main_balance = Column(DECIMAL(10, 2))
    referral_balance = Column(DECIMAL(10, 2))
    bonus_balance = Column(DECIMAL(10, 2))

    user = relationship("User", back_populates="account")
