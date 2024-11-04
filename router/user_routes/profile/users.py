from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.user.user import User
from schema.users import UserBase
from ..auth.auth import Auth

auth = Auth()


class Users:
    def __init__(self, db_session: Session, user_id: int):
        self.db_session = db_session
        self.user_id = user_id

    def get_user(self):
        return self.db_session.query(User).filter(User.id == self.user_id).first()

    def edit_user(self, data: UserBase):
        user = self.get_user()
        if user:
            for key, value in data:
                setattr(user, key, value)
            self.db_session.commit()
            return {"status": "success", "data": data}
        else:
            return None

    def change_password(self, new_password: str, old_password: str):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user = self.get_user()
        if user:
            old_password = pwd_context.verify(old_password, user.password)
            if old_password:
                user.password = pwd_context.hash(new_password)
                self.db_session.commit()
                return {"status": "success", "data": user}
        else:
            raise HTTPException(status_code=404, detail="Incorrect password")

    def deactivate_account(self):
        user = self.get_user()
        user.is_active = False
        self.db_session.commit()
        return {"status": "success"}

