from sqlalchemy import Column, Enum, Integer, ForeignKey, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_type = Column(Enum('deposit', 'withdraw', name='transaction_type_enum'), nullable=False)
    transaction_amount = Column(DECIMAL(10, 2))
    transaction_method = Column(Enum('card-payment', 'bank-transfer', 'cryptocurrency', name='transaction_method_enum'), nullable=False)
    status = Column(Enum('pending', 'processing', 'approved', 'not approved', name='status_enum'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="transactions")
