from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests

from database import SessionLocal
from .users import Users
from dependencies import get_token_header
from schema.users import UserBase

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users/")
async def get_user(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    users = Users(db, user_id)
    user = users.get_user()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/users/")
async def edit_user(data: UserBase = Depends(), token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    users = Users(db, user_id)
    updated_user = users.edit_user(data)
    if updated_user:
        return updated_user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/users/change-password/")
async def change_password(new_password: str, old_password: str, token_payload: dict = Depends(get_token_header),
                          db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    users = Users(db, user_id)
    updated_user = users.change_password(new_password, old_password)
    if updated_user:
        return updated_user
    else:
        return HTTPException(status_code=404, detail=f"Unable to change password")


@router.post("/users/delete-user/")
async def delete_user(token_payload: dict = Depends(get_token_header), db: Session = Depends(get_db)):
    user_id = token_payload.get("data")
    users = Users(db, user_id)
    try:
        delete_user_ = users.deactivate_account()
        return delete_user_
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"User not found {e}")
