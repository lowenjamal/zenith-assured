from passlib.context import CryptContext
import datetime
from sqlalchemy import desc
from fastapi import HTTPException
from fastapi.responses import FileResponse
from models.user import user, account, trading
from models.user.transactions import Transaction
from models.user.verification_document import DocumentVerification
from schema import users, make_transaction_admin
from sqlalchemy.orm import Session
import os
from decimal import Decimal

SECRET_KEY = os.getenv("JWT_SECRET_TOKEN")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 300


class UserManagement:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_all_user(self, admin_id: int):
        user_ = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
        if user_.user_type == "super_admin":
            return self.db_session.query(user.User).filter(
                user.User.is_active,
                user.User.user_type == 'customer'
            ).order_by(desc(user.User.created_at)).all()
        if user_.user_type == "admin":
            return self.db_session.query(user.User).filter(
                user.User.is_active,
                user.User.assigned_to == admin_id
            ).all()

    def view_user(self, user_id: int, admin_id: int):
        user_ = self.db_session.query(user.User).filter(user.User.id == user_id).first()
        trading_activities = self.db_session.query(trading.TradeTable).filter(
            trading.TradeTable.user_id == user_id).order_by(desc(trading.TradeTable.created_at)).all()
        transaction_activities = self.db_session.query(Transaction).filter(
            Transaction.user_id == user_id).order_by(desc(Transaction.created_at)).all()
        accounts = self.db_session.query(account.Account).filter(
            account.Account.user_id == user_id).all()
        admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
        response = [
            {'user': user_},
            {'trading activities': trading_activities},
            {'transaction_activities': transaction_activities},
            {'accounts': accounts}
        ]
        if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
            if user_:
                return response
        else:
            raise HTTPException(status_code=401, detail="You do not have access to this user")

    async def login_user_account(self, user_id: int, admin_id: int):
        user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                        user.User.user_type == 'customer').first()
        admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
        if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
            return user_
        else:
            raise HTTPException(status_code=401, detail="You do not have access to this user")

    def reset_user_password(self, user_id: int, admin_id: int):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            hashed_password = self.pwd_context.hash("default123")
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                user_.password = hashed_password
                self.db_session.commit()
                return {"status": "success", "message": "Password reset Successfully"}
            else:
                raise HTTPException(status_code=401, detail="You do not have access to this user")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=401, detail={"status": "error", "message": str(e)})

    def edit_user(self, user_id: int, admin_id: int, user_details: users.UserBase):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                for key, value in user_details:
                    setattr(user_, key, value)
                self.db_session.commit()
                return {"status": "success", "data": user_details}
            else:
                raise HTTPException(status_code=401, detail="You do not have access to this user")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=401, detail={"status": "error", "message": str(e)})

    def deactivate_user_account(self, user_id: int, admin_id: int):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                if user_:
                    user_.is_active = False
                    self.db_session.commit()
                    return {"status": "success", "message": f"User {user_.first_name} deactivated successfully."}
                else:
                    return {"status": "error", "message": f"User {user_.first_name} not found or not a customer."}
            else:
                raise HTTPException(status_code=401, detail="You do not have access to this user")
        except Exception as e:
            self.db_session.rollback()
            return {"status": "error", "message": f"Failed to deactivate user {user_id}: {str(e)}"}

    def get_all_verification_documents(self, user_id: int, admin_id: int):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                get_document = self.db_session.query(DocumentVerification).filter(
                    DocumentVerification.user_id == user_id).order_by(desc(DocumentVerification.created_at)).all()
                return {"status": "success", "message": get_document}
        except Exception as e:
            raise HTTPException(status_code=401,
                                detail={"status": "error", "message": f"Unable to fetch file: {str(e)}"})

    def view_verification_document(self, user_id: int, admin_id: int, file_id: int):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                document = self.db_session.query(DocumentVerification).filter(
                    DocumentVerification.user_id == user_id, DocumentVerification.id == file_id).first()
                if not document:
                    raise HTTPException(status_code=404, detail="Verification document not found")
                front_path = document.front_document_path
                back_path = document.back_document_path
                if not os.path.exists(front_path):
                    raise HTTPException(status_code=404, detail="Front document not found")
                if back_path and not os.path.exists(back_path):
                    raise HTTPException(status_code=404, detail="Back document not found")
                if back_path:
                    return FileResponse(front_path, media_type="image/jpeg"), FileResponse(back_path,
                                                                                           media_type="image/jpeg")
                else:
                    return FileResponse(front_path, media_type="image/jpeg")
        except Exception as e:
            raise HTTPException(status_code=401,
                                detail={"status": "error", "message": f"Unable to fetch file: {str(e)}"})

    def change_verification_status(self, user_id: int, admin_id: int,
                                   status: make_transaction_admin.IdVerificationEnum):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                match status:
                    case status.unverified:
                        user_.id_verified = "unverified"
                    case status.verifying:
                        user_.id_verified = "verifying"
                    case status.verified:
                        user_.id_verified = "verified"
                    case _:
                        raise ValueError("Invalid option chosen")
                self.db_session.commit()
                return {"status": "success", "message": f"Status changed to {status.value}"}
        except Exception as e:
            raise HTTPException(status_code=401,
                                detail={"status": "error",
                                        "message": f"Unable to change verification status: {str(e)}"})

    def change_transaction_status(self, status: str, transaction_id: int, user_id: int, admin_id: int):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            transaction_ = self.db_session.query(Transaction).filter(
                Transaction.id == transaction_id).first()  # Use transactions.Transaction here
            account_ = self.db_session.query(account.Account).filter(account.Account.user_id == user_id).first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                if status == "processing":
                    transaction_.status = "processing"
                elif status == "not approved":
                    transaction_.status = "processing"
                elif status == "approved":
                    if transaction_.transaction_type == "deposit":
                        account_.main_balance += Decimal(transaction_.transaction_amount)
                        transaction_.status = "approved"
                    elif transaction_.transaction_type == "withdraw":
                        account_.main_balance -= Decimal(transaction_.transaction_amount)
                        transaction_.status = "approved"
                self.db_session.commit()
            else:
                raise HTTPException(status_code=401, detail="You do not have access to this user")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=401, detail={"status": "error", "message": str(e)})

    def make_transaction(self, user_id: int, amount: float, balance_type: str, transaction_type: str, admin_id: int):
        try:

            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            account_ = self.db_session.query(account.Account).filter(account.Account.user_id == user_id).first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                if transaction_type == "deposit":
                    match balance_type:
                        case "main_balance":
                            account_.main_balance += Decimal(amount)
                        case "referral_balance":
                            account_.referral_balance += Decimal(amount)
                        case "bonus_balance":
                            account_.bonus_balance += Decimal(amount)
                        case _:
                            raise ValueError("Invalid Balance")
                if transaction_type == "withdraw":
                    match balance_type:
                        case "main_balance":
                            if amount >= account_.main_balance:
                                account_.main_balance -= Decimal(amount)
                            else:
                                raise HTTPException(status_code=401, detail="Insufficient main balance")
                        case "referral_balance":
                            if amount >= account_.referral_balance:
                                account_.referral_balance -= Decimal(amount)
                            else:
                                raise HTTPException(status_code=401, detail="Insufficient main balance")
                        case "bonus_balance":
                            if amount >= account_.bonus_balance:
                                account_.bonus_balance -= Decimal(amount)
                            else:
                                raise HTTPException(status_code=401, detail="Insufficient main balance")
                        case _:
                            raise ValueError("Invalid Balance")

                make_transaction_ = Transaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    transaction_amount=Decimal(amount),
                    status="approved",
                    transaction_method="bank-transfer",
                    created_at=datetime.datetime.now()
                )
                self.db_session.add(make_transaction_)
                self.db_session.commit()
                self.db_session.refresh(make_transaction_)
                return {"status": "success", "message": make_transaction_}
            else:
                raise HTTPException(status_code=401, detail="You do not have access to this user")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=401, detail={"status": "error", "message": str(e)})

    def add_custom_profit(self, user_id: int, admin_id: int, trade_id: int, profit: float):
        try:
            user_ = self.db_session.query(user.User).filter(user.User.id == user_id,
                                                            user.User.user_type == 'customer').first()
            admin_user = self.db_session.query(user.User).filter(user.User.id == admin_id).first()
            if admin_user.user_type == "super_admin" or user_.assigned_to == admin_id:
                trade_ = self.db_session.query(trading.TradeTable).filter(trading.TradeTable.id == trade_id).first()
                if trade_:
                    trade_.profit = profit
                    self.db_session.commit()
                    self.db_session.refresh(trade_)
            else:
                raise HTTPException(status_code=401, detail="You do not have access to this user")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=401, detail={"status": "error", "message": str(e)})
