from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user.account import Account


async def account_task(task: str, amount: float, user_id: int, db: Session):
    response = {"status": "success"}
    try:
        account = db.query(Account).filter(Account.user_id == user_id).first()
        if account:
            match task:
                case "create":
                    if account.main_balance > amount:
                        account.main_balance = account.main_balance - amount
                    else:
                        response = {"status": "error", "message": "Insufficient amount to open trade"}
                case "close":
                    account.main_balance = account.main_balance + amount
            db.commit()
            return response
    except HTTPException:
        raise HTTPException(status_code=403, detail="Error making transaction")
