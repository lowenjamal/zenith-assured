from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from dependencies import get_token_header
from .transactions_class import TransactionClass
from models.user import transactions
from schema.transactions import TransactionCreate
from schema import finance_details

transactions.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.get("/get-transactions/")
async def get_transactions(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    transaction_ = TransactionClass(db, user_id)
    transactions_ = transaction_.get_transaction()
    if transactions_:
        return [{"status": "success"}, {"data": transactions_}]
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")


@router.get("/get-payment-details")
async def get_finance_details(key: str, token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    try:
        if key == "Less Loved":
            user_id = token_payload.get("data")
            data = TransactionClass(db, user_id).get_finance_details()
            if data:
                return data
            else:
                raise HTTPException(status_code=404, detail="Unable to fetch Bank Details")
        else:
            raise HTTPException(status_code=401, detail="Nice try!! You can't access this without the right key")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/deposit-transaction/")
async def deposit_transactions(transaction_data: TransactionCreate, card_data: finance_details.CardDetailsCreate, token_payload: dict = Depends(get_token_header),
                               db: Session = Depends(get_db)):
    if transaction_data.transaction_amount < 5:
        return [{"status": "error"}, {"data": "amount must be greater than 5"}]
    user_id = token_payload.get("data")
    transaction_ = TransactionClass(db, user_id)
    transactions_ = transaction_.create_deposit_transaction(transaction_data, card_data)
    if transactions_:
        return [{"status": "success"}, {"data": transactions_}]
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")


@router.post("/withdraw-transaction")
async def withdraw_transaction(transaction_data: TransactionCreate, ls, card_details_data: finance_details.CardDetailsCreate, bank_details_data: finance_details.BankDetailsCreate,  token_payload: dict = Depends(get_token_header),
                               db: Session = Depends(get_db)):
    if transaction_data.transaction_amount < 5:
        return [{"status": "error"}, {"data": "amount must be greater than 5"}]
    user_id = token_payload.get("data")
    transaction_ = TransactionClass(db, user_id)
    transactions_ = transaction_.create_withdraw_transaction(transaction_data, crypto_data, card_details_data, bank_details_data)
    if transactions_:
        return [{"status": "success"}, {"data": transactions_}]
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")
