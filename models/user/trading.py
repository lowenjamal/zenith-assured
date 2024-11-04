from sqlalchemy import Column, ForeignKey, Integer, Float, Enum, String, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class TradeTable(Base):
    __tablename__ = "trade_table"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    asset_pair_type = Column(String(255))
    trade_type = Column(Enum('limit', 'market', name="trade_type_enum"))
    amount = Column(DECIMAL(10, 2))
    trade_transaction_type = Column(Enum('buy', 'sell', name='trade_transaction_type_enum'))
    profit = Column(Float, default=0.00)
    created_by = Column(Enum('self', 'account-manager', 'auto-trader', name='created_by_enum'))
    status = Column(Enum('open', 'closed', 'cancelled', name='trade_status_type'))
    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="trading")
