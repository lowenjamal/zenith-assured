import random
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import Session
from models.user.trading import TradeTable
from models.user.account import Account
from models.user.user import User
from schema.trading import TradeTableCreate, TradeStatusEnum
from ..helpers import account_task
from decimal import Decimal


class TraderClass:
    def __init__(self, db_session: Session, user_id: int):
        self.db_session = db_session
        self.user_id = user_id

    def get_all_trade(self):
        return self.db_session.query(TradeTable).filter(TradeTable.user_id == self.user_id).order_by(
            desc(TradeTable.created_at)).all()

    def activate_auto_trader(self):
        user = self.db_session.query(User).filter(User.id == self.user_id).first()
        user.can_auto_trade = not user.can_auto_trade
        self.db_session.commit()
        self.db_session.refresh(user)
        return {"status": "success", "message": "auto-trade status changed"}

    async def create_trade(self, trading_data: TradeTableCreate):
        try:
            make_transaction = await account_task(task="create", amount=Decimal(trading_data.amount), user_id=self.user_id,
                                                  db=self.db_session)
            user = self.db_session.query(Account).filter(Account.user_id == self.user_id).first()

            def make_profit():
                profit_ = 0.00
                match user.account_type:
                    case 'basic':
                        profit_ = round(random.uniform(-0.50, 0.90), 2)
                    case 'premium':
                        profit_ = round(random.uniform(0.50, 1.90), 2)
                    case 'gold':
                        profit_ = round(random.uniform(2.00, 2.80), 2)
                    case 'premium':
                        profit_ = round(random.uniform(2.50, 4.00), 2)
                return profit_

            if make_transaction["status"] == "success":
                create_trade = TradeTable(
                    user_id=self.user_id,
                    asset_pair_type=trading_data.asset_pair_type,
                    trade_type=trading_data.trade_type,
                    amount=trading_data.amount,
                    trade_transaction_type=trading_data.trade_transaction_type,
                    profit=make_profit(),
                    status=TradeStatusEnum.open,
                    created_by=trading_data.created_by.self,
                    created_at=datetime.now()
                )
                self.db_session.add(create_trade)
                self.db_session.commit()
                return create_trade
            else:
                return make_transaction
        except Exception as e:
            raise e

    async def close_trade(self, trade_id: int):
        query = self.db_session.query(TradeTable).filter(TradeTable.id == trade_id).first()
        account = self.db_session.query(Account).filter(Account.user_id == self.user_id).first()
        if query.status != "closed":
            account.main_balance = Decimal(account.main_balance) + Decimal(
                Decimal(query.amount) + (Decimal(query.amount) * Decimal(query.profit)))
            query.status = TradeStatusEnum.closed
            self.db_session.commit()
            self.db_session.refresh(query)
            self.db_session.refresh(account)
            return query
