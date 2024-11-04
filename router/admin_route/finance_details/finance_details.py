from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.user import finance_details_table
from schema import finance_details
from .finance_details_class import FinanceDetails
from database import engine, SessionLocal

finance_details_table.Base.metadata.create_all(bind=engine)
KEY = "Less Loved"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/create-bank-details/")
async def create_bank_details(key: str, bank_data: finance_details.BankDetailsCreate = Depends(),
                              db: Session = Depends(get_db)):
    try:
        create_bank = FinanceDetails(db)
        if key == KEY:
            data = create_bank.create_bank_details(bank_data)
            if data["status"] == "success":
                return data
            else:
                raise HTTPException(status_code=401, detail="Error creating bank details, bank details alread exist for admin")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.put("/edit-bank-details/{bank_id}/")
async def edit_bank_details(key: str, bank_id: int, bank_data: finance_details.BankDetailsCreate,
                            db: Session = Depends(get_db)):
    try:
        if key == KEY:
            data = FinanceDetails(db).edit_bank_details(bank_id, bank_data)
            if data["status"] == "success":
                return data
            else:
                raise HTTPException(status_code=401, detail="Error editing bank details")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/create-crypto-details/")
async def create_crypto_details(key: str, crypto_data: finance_details.CryptoCurrencyWalletCreate,
                                db: Session = Depends(get_db)):
    try:
        if key == KEY:
            data = FinanceDetails(db).create_crypto_payment_details(crypto_data)
            if data["status"] == "success":
                return data
            else:
                raise HTTPException(status_code=401, detail="Error editing bank details")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.put("/edit-crypto-details/{crypto_id}")
async def edit_crypto_details(key: str, crypto_id: int, crypto_data: finance_details.CryptoCurrencyWalletCreate,
                              db: Session = Depends(get_db)):
    try:
        if key == KEY:
            data = FinanceDetails(db).edit_crypto_payment_details(crypto_id, crypto_data)
            if data["status"] == "success":
                return data
            else:
                raise HTTPException(status_code=401, detail="Error editing bank details")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
