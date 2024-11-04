from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from .user_class import UserManagement
from dependencies import get_token_header
from database import SessionLocal
from ..helpers import create_access_token
from schema.make_transaction_admin import MakeTransaction, IdVerificationEnum
from schema.transaction_status_admin import TransactionStatus
from schema import users

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 300


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/get-all-users/")
async def get_all_users(token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    admin_id = token_header.get("data")
    get_user = UserManagement(db)
    return get_user.get_all_user(admin_id)


@router.get("/view-user/{user_id}/")
async def view_user(user_id: int, token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    admin_id = token_header.get("data")
    view_user_ = UserManagement(db)
    return view_user_.view_user(user_id, admin_id)


@router.post("/login-user/{user_id}")
async def login_user(user_id: int, token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    admin_id = token_header.get("data")
    log_user = await UserManagement(db).login_user_account(user_id, admin_id)
    if not log_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'data': int(log_user.id), 'user_type': log_user.user_type},
                                       expires_delta=access_token_expires)
    return {"status": "success", "access-token": access_token}


@router.post("/deactivate-user/{user_id}")
async def deactivate_user(user_id: int, token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    try:
        admin_id = token_header.get("data")
        deactivate_user_ = UserManagement(db).deactivate_user_account(user_id, admin_id)
        return deactivate_user_
    except Exception as e:
        return {'status': 'error', 'details': e}


@router.post("/reset-user-password/{user_id}")
async def reset_user_password(user_id: int, token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    try:
        admin_id = token_header.get("data")
        reset_password = UserManagement(db).reset_user_password(user_id, admin_id)
        return reset_password
    except Exception as e:
        return {'status': 'error', 'details': e}


@router.post("/edit-user-details/{user_id}")
async def reset_user_password(user_id: int, user_details: users.UserBase, token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    try:
        admin_id = token_header.get("data")
        edit_user = UserManagement(db).edit_user(user_id, admin_id, user_details)
        return edit_user
    except Exception as e:
        return {'status': 'error', 'details': e}


@router.get("/get-verification-document/{user_id}")
async def get_verification_documents(user_id: int, token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    admin_id = token_header.get("data")
    get_documents = UserManagement(db).get_all_verification_documents(user_id, admin_id)
    return get_documents


@router.get("/view-verification-document/{user_id}/")
async def view_verification_document(user_id: int, file_id: int, token_header=Depends(get_token_header),
                                     db: Session = Depends(get_db)):
    admin_id = token_header.get("data")
    view_document = UserManagement(db).view_verification_document(user_id, admin_id, file_id)
    return view_document


@router.put("/change-verification-status/{user_id}")
async def change_verification_status(user_id: int, status_: IdVerificationEnum, token_header=Depends(get_token_header),
                                     db: Session = Depends(get_db)):
    admin_id = token_header.get("data")
    verify_user = UserManagement(db).change_verification_status(user_id, admin_id, status_)
    return verify_user


@router.post("/make-transaction/")
async def create_transaction(transaction_data: MakeTransaction = Depends(), token_header=Depends(get_token_header),
                             db: Session = Depends(get_db)):
    try:
        admin_id = token_header.get("data")
        transactions_ = UserManagement(db)
        result = transactions_.make_transaction(transaction_data.user_id, transaction_data.amount,
                                                transaction_data.balance_type,
                                                transaction_data.transaction_type, admin_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.put("/change-transaction-status/{transaction_id}")
async def update_transaction_status(transaction_id: int, user_id: int, status_: TransactionStatus,
                                    token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    try:
        admin_id = token_header.get("data")
        change_status = UserManagement(db)
        result = change_status.change_transaction_status(status_.value, transaction_id, user_id, admin_id)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/add-custom-profit/{trade_id}")
async def add_custom_profit(user_id: int, trade_id, profit,
                            token_header=Depends(get_token_header), db: Session = Depends(get_db)):
    try:
        admin_id = token_header.get("data")
        add_profit = UserManagement(db)
        result = add_profit.add_custom_profit(user_id, admin_id, trade_id, profit)
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
