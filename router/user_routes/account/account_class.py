from sqlalchemy.orm import Session
from models.user.account import Account
from schema.account import AccountTypeEnum
from models.user.user import User


class AccountClass:
    def __init__(self, db_session: Session, user_id: int):
        self.db_session = db_session
        self.user_id = user_id

    def create_account(self):
        db_account = Account(
            user_id=self.user_id,
            account_type=AccountTypeEnum.basic,
            main_balance=0,
            referral_balance=0,
            bonus_balance=0
        )
        self.db_session.add(db_account)
        self.db_session.commit()
        self.db_session.refresh(db_account)
        return db_account

    def get_account(self):
        return self.db_session.query(Account).filter(Account.user_id == self.user_id).first()

    # def withdraw_main_balance(self, amount: int):
    #     account = self.get_account()
    #     if account:
    #         if account.main_balance > 0:
    #             if amount <= account.main_balance:
    #                 # Set withdrawal limits based on account type
    #                 withdrawal_limit = None
    #                 account_type = account.account_type
    #                 if account_type == "basic":
    #                     withdrawal_limit = 50  # Define withdrawal limit for basic accounts
    #                 elif account_type == "premium":
    #                     withdrawal_limit = 1000  # Define withdrawal limit for premium accounts
    #                 elif account_type == "gold":
    #                     withdrawal_limit = 3000  # Define withdrawal limit for gold accounts
    #                 elif account_type == "platinum":
    #                     withdrawal_limit = 5000  # Define withdrawal limit for platinum accounts
    #
    #                 # Check if the withdrawal amount exceeds the withdrawal limit
    #                 if withdrawal_limit is not None and amount > withdrawal_limit:
    #                     return {"message": "Withdrawal amount exceeds limit"}
    #
    #                 # Perform withdrawal operation
    #                 # (Implementation of withdrawal operation goes here)
    #                 return {"message": "Withdrawal successful"}
    #             else:
    #                 return {"message": "Insufficient balance"}
    #         else:
    #             return {"status": "error", "message": "Your balance is Zero"}
