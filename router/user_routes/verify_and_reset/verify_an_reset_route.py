from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from dependencies import get_token_header
from .verify_and_reset_class import VerifyAndReset

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/send-verification-email/")
async def send_verification_email(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    try:
        user_id = token_payload.get("data")
        email = VerifyAndReset(db_session=db).send_verification_email(user_id=user_id)
        if email:
            return email
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Unable to send verification email {str(e)}")


@router.get("/verify-email/")
async def verify_email(email_token: str, db: Session = Depends(get_db)):
    try:
        email = VerifyAndReset(db_session=db).verify_user(token=email_token)
        if email:
            return email
    except Exception as e:
        raise HTTPException(status_code=404, detail="Unable to verify email")


@router.post("/send-reset-password/")
async def send_reset_password(email: str, db: Session = Depends(get_db)):
    try:
        reset = VerifyAndReset(db_session=db).send_reset_password_email(email=email)
        return reset
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Unable to send reset password email {str(e)}")


@router.put("/reset-password/")
async def reset_password(email_token: str, password: str,  db: Session = Depends(get_db)):
    try:
        reset = VerifyAndReset(db_session=db).reset_password(token=email_token, password=password)
        return reset
    except Exception as e:
        raise HTTPException(status_code=404, detail="Unable to send reset password email")

