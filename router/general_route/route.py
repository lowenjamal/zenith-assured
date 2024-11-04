from fastapi import APIRouter, HTTPException, Depends
from models.user.user import User
from models.user.account import Account
from sqlalchemy.orm import Session
from database import SessionLocal
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from typing import Optional
from jose import jwt

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_TOKEN")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 300


class AdsUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    country: str
    bonus_amount: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/create-new-user-from-ads")
async def create_user_from_ads(user_data: AdsUser = Depends(), db: Session = Depends(get_db)):
    try:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("default123")
        ad_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password=hashed_password,
            address="Not provided",
            country=user_data.country,
            phone_number=user_data.phone_number,
            date_of_birth=datetime.now(),
            user_type="customer",
            created_at=datetime.now()
        )
        db.add(ad_user)
        db.commit()
        db.refresh(ad_user)
        create_account = Account(
            user_id=ad_user.id,
            account_type="basic",
            main_balance=0,
            referral_balance=0,
            bonus_balance=user_data.bonus_amount
        )
        db.add(create_account)
        db.commit()
        db.refresh(create_account)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"data": int(ad_user.id), 'user_type': ad_user.user_type},
                                           expires_delta=access_token_expires)
        return {"status": "success", "message": access_token}
    except Exception as e:
        raise HTTPException(status_code=403, detail={"message": "Unable to create user", "more details": str(e)})
