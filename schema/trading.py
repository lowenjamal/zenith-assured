from pydantic import BaseModel
from enum import Enum


class TradeTypeEnum(str, Enum):
    limit = 'limit'
    market = 'market'


class TradeStatusEnum(str, Enum):
    open = 'open'
    closed = 'closed'
    cancelled = 'cancelled'


class CreatedByEnum(str, Enum):
    self = 'self'
    account_manager = 'account-manager'
    auto_trader = 'auto-trader'


class TradeTransactionTypeEnum(str, Enum):
    buy = 'buy',
    sell = 'sell'


class TradeTableBase(BaseModel):
    asset_pair_type: str
    amount: float


class TradeTableCreate(TradeTableBase):
    trade_type: TradeTypeEnum
    created_by: CreatedByEnum
    trade_transaction_type: TradeTransactionTypeEnum


class TradeTableUpdate(BaseModel):
    status: TradeStatusEnum


class TradeTable(TradeTableBase):
    id: int

    class Config:
        orm_mode = True
