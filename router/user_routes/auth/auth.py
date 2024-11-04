import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.user.user import User
from models.crm.leads import CRMUserBase
from schema.users import UserCreate, UserTypeEnum


load_dotenv()


class Auth:
    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register_user(self, user_data: UserCreate, db: Session):
        hashed_password = self.pwd_context.hash(user_data.password)
        db_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password=hashed_password,
            address=user_data.address,
            country=user_data.country,
            phone_number=user_data.phone_number,
            date_of_birth=user_data.date_of_birth,
            user_type=UserTypeEnum.customer,
            created_at=datetime.now()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def login_user(self, email: str, password: str, db: Session):
        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )
        if user and self.verify_password(password, user.password):
            if user.is_active:
                return user
            else:
                return {"status": "account deleted"}
        return None
