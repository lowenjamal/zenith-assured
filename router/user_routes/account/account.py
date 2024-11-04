from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from dependencies import get_token_header
from .account_class import AccountClass
from models.user import account

account.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


async def create_account(user_id: int, db: Session):
    account_ = AccountClass(db, user_id)
    if account_:
        account_.create_account()
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/get-account/")
async def get_account(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    accounts_ = AccountClass(db, user_id)
    account_ = accounts_.get_account()
    if account_:
        return account_
    else:
        raise HTTPException(status_code=404, detail="Account not found")

# @router.post("/withdraw/")
# async def withdraw(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
#     user_id = token_payload.get("user_id")
#     accounts_ = AccountClass(db, user_id)
#     pass
