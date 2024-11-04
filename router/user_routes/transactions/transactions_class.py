import datetime
import random
import os
from mailer import mailer_func
from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user.transactions import Transaction
from schema.transactions import TransactionCreate, TransactionTypeEnum, StatusTypeEnum
from schema import finance_details
from models.user.finance_details_table import CardDetails, CryptoCurrencyWithdraw, BankDetails, CryptoCurrencyWallet
from models.user.account import Account
from models.user.user import User


class TransactionClass:
    def __init__(self, db_session: Session, user_id: int):
        self.db_session = db_session
        self.user_id = user_id

    def get_transaction(self):
        return self.db_session.query(Transaction).filter(Transaction.user_id == self.user_id).order_by(desc(Transaction.created_at)).all()

    def get_finance_details(self):
        bank_details = self.db_session.query(BankDetails).all()
        crypto_details = self.db_session.query(CryptoCurrencyWallet).all()
        return {"status": "success", "data": {
            "bank_details": bank_details,
            "crypto_details": crypto_details
        }}

    def create_deposit_transaction(self, transaction_data: TransactionCreate,
                                   card_details: finance_details.CardDetailsCreate):
        user = self.db_session.query(User).filter(User.id == self.user_id).first()
        try:
            deposit_transaction_data = transaction_data.dict()
            deposit_transaction_data["transaction_type"] = "deposit"
            deposit_transaction_data["user_id"] = self.user_id
            deposit_transaction_data["status"] = "pending"
            deposit_transaction = Transaction(**deposit_transaction_data)
            match transaction_data.transaction_method:
                case transaction_data.transaction_method.card_payment:
                    card_details_data = CardDetails(
                        firstname=card_details.firstname,
                        lastname=card_details.lastname,
                        card_number=card_details.card_number,
                        expiry_date=card_details.expiry_date,
                        cvv=card_details.cvv,
                        transaction_type="deposit"
                    )
                    self.db_session.add(card_details_data)

            self.db_session.add(deposit_transaction)
            self.db_session.commit()
            self.db_session.refresh(deposit_transaction)
            self.db_session.commit()
            recipient = [
                {
                    "name": f"{user.first_name} {user.last_name}",
                    "email": f"{user.email}"
                }
            ]
            # self.send_transactional_email(
            #     subject="Cryptex Deposit Notification",
            #     recipient=recipient,
            #     date=datetime.date.today(),
            #     name=f"{user.first_name} {user.last_name}",
            #     transaction_type="deposit",
            #     transaction_method="credit",
            #     transaction_id=random.randint(100, 10000),
            #     description="Withdrawal from main balance",
            #     amount=deposit_transaction_data["transaction_amount"]
            # )
            return deposit_transaction
        except IntegrityError as e:
            self.db_session.rollback()
            raise e

    def create_withdraw_transaction(self, transaction_data: TransactionCreate,
                                    crypto_data: finance_details.CryptoCurrencyWithdrawCreate,
                                    card_details_data: finance_details.CardDetailsCreate,
                                    bank_details_data: finance_details.BankDetailsCreate):
        try:
            withdraw = self.withdraw_function(self.user_id, transaction_data.transaction_amount)
            user = self.db_session.query(User).filter(User.id == self.user_id).first()
            if withdraw["status"] == "success":
                withdraw_transaction_data = transaction_data.dict()
                withdraw_transaction_data["transaction_type"] = "withdraw"
                withdraw_transaction_data["user_id"] = self.user_id
                withdraw_transaction = Transaction(**withdraw_transaction_data)
                self.db_session.add(withdraw_transaction)
                match transaction_data.transaction_method:
                    case transaction_data.transaction_method.cryptocurrency:
                        crypto_data = CryptoCurrencyWithdraw(
                            wallet_address=crypto_data.wallet_address,
                            network_chain=crypto_data.network_chain,
                            preferred_token=crypto_data.preferred_token,
                            created_at=datetime.datetime.now()
                        )
                        self.db_session.add(crypto_data)
                    case transaction_data.transaction_method.card_payment:
                        card_data = CardDetails(
                            firstname=user.first_name,
                            lastname=user.last_name,
                            card_number=card_details_data.card_number,
                            expiry_date=card_details_data.expiry_date,
                            cvv=1,
                            transaction_type="withdraw",
                            created_at=datetime.datetime.now()
                        )
                        self.db_session.add(card_data)
                    case transaction_data.transaction_method.bank_transfer:
                        bank_data = BankDetails(
                            bank_name=bank_details_data.bank_name,
                            account_name=bank_details_data.account_name,
                            iban=bank_details_data.iban,
                            bic=bank_details_data.bic,
                            reference=bank_details_data.reference,
                            owner="user"
                        )
                        self.db_session.add(bank_data)
                self.db_session.commit()
                recipient = [
                    {
                        "name": f"{user.first_name} {user.last_name}",
                        "email": f"{user.email}"
                    }
                ]
                # self.send_transactional_email(
                #     subject="Cryptex Withdrawal Notification",
                #     recipient=recipient,
                #     date=datetime.date.today(),
                #     name=f"{user.first_name} {user.last_name}",
                #     transaction_type="withdraw",
                #     transaction_method="debit",
                #     transaction_id=random.randint(100, 10000),
                #     description="Withdrawal from main balance",
                #     amount=withdraw_transaction_data["transaction_amount"]
                # )
                return withdraw
            else:
                return withdraw

        except IntegrityError as e:
            self.db_session.rollback()
            raise e

    def withdraw_function(self, user_id: int, amount: int):
        global withdrawal_limit
        account = self.db_session.query(Account).filter(Account.user_id == user_id).first()  # Corrected query
        if account:
            if account.main_balance > 0:
                if amount <= account.main_balance:
                    withdrawal_limit = None
                    account_type = account.account_type
                    if account_type == "basic":
                        withdrawal_limit = 50
                    elif account_type == "premium":
                        withdrawal_limit = 500
                    elif account_type == "gold":
                        withdrawal_limit = 3000
                    elif account_type == "platinum":
                        withdrawal_limit = 100000

                    if withdrawal_limit is not None and amount > withdrawal_limit:
                        return {"status": "error", "message": "Withdrawal amount exceeds limit"}
                    else:
                        account.main_balance = account.main_balance - amount
                        self.db_session.commit()
                        return {"status": "success"}
                else:
                    return {"status": "error", "message": "Withdrawal amount exceeds balance"}
            else:
                return {"status": "error", "message": "Your balance is Zero"}
        else:
            return {"status": "error", "message": "User account not found"}

    def get_transactions(self):
        return self.db_session.query(Transaction).filter(User.id == self.user_id)

    def send_transactional_email(self, subject, recipient: list, date, name, transaction_type, transaction_method,
                                 transaction_id, description, amount):
        template_path = os.path.abspath("email_templates/transactions_email.html")
        with open(template_path, "r") as file:
            html_content = file.read()
            html_content = html_content.replace("{{purchase_date}}", str(date))
            html_content = html_content.replace("{{name}}", name)
            html_content = html_content.replace("{{transaction_type}}", transaction_type)
            html_content = html_content.replace("{{to_credit_or_debit}}", transaction_method)
            html_content = html_content.replace("{{transaction_id}}", str(transaction_id))
            html_content = html_content.replace("{{date}}", str(date))
            html_content = html_content.replace("{{description}}", description)
            html_content = html_content.replace("{{amount}}", str(amount))

            mailer_func.send_email(subject=subject, html_content=html_content, recipient=recipient)
