from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
import os
from dotenv import load_dotenv
from ..account.account import create_account
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from .auth import Auth
from database import engine, SessionLocal
from schema.users import UserCreate, UserLogin
from models.user import user
from mailer import mailer_func
from .helpers import create_access_token
from datetime import timedelta
from ..verify_and_reset.verify_and_reset_class import VerifyAndReset

user.Base.metadata.create_all(bind=engine)

load_dotenv()

# to get random secret key:
# openssl rand -hex 32
SECRET_KEY = os.getenv("JWT_SECRET_TOKEN")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 300

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


def get_session_local():
    yield SessionLocal()


def get_auth(db: Session = Depends(get_session_local)):
    return Auth(db_session=db)


@router.post("/register/")
async def user_register(user_data: UserCreate = Depends(), auth: Auth = Depends(get_auth),
                        db: Session = Depends(get_session_local)):
    try:
        user_reg = auth.register_user(user_data, db)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"data": int(user_reg.id), 'user_type': user_reg.user_type},
                                           expires_delta=access_token_expires)

        def send_registration_email(subject, recipient_: list, name, company_name, verify_url, login_url, user_email,
                                    dashboard_url, support_email):
            template_path = os.path.abspath("email_templates/register_email.html")
            with open(template_path, "r") as file:
                html_content = file.read()
                html_content = html_content.replace("{{name}}", name)
                html_content = html_content.replace("{{company_name}}", company_name)
                html_content = html_content.replace("{{verify_url}}", verify_url)
                html_content = html_content.replace("{{login_url}}", login_url)
                html_content = html_content.replace("{{user_email}}", user_email)
                html_content = html_content.replace("{{dashboard_url}}", dashboard_url)
                html_content = html_content.replace("{{support_email}}", support_email)

                mailer_func.send_email(subject=subject, html_content=html_content, recipient=recipient_)

        create_account_ = await create_account(user_reg.id, db)
        if create_account_["status"] == "success":
            response = access_token
            recipient = [
                {
                    "name": f"{user_reg.first_name} {user_reg.last_name}",
                    "email": f"{user_reg.email}"
                }
            ]
            user_data = {"id": user_reg.id, "created_at": user_reg.verified}
            verify_token = VerifyAndReset(db_session=db).create_email_token(user_data)
            # send_registration_email(
            #     subject="FinnoVent Capital Registration Notification",
            #     recipient_=recipient,
            #     name=f"{user_reg.first_name} {user_reg.last_name}",
            #     company_name="FinnoVent Capital",
            #     verify_url=f"{os.getenv('FRONTEND_URL')}/dashboard/verify-email/?{verify_token}",
            #     login_url=f"{os.getenv('FRONTEND_URL')}/login",
            #     user_email=f"{user_reg.email}",
            #     dashboard_url=f"{os.getenv('FRONTEND_URL')}/dashboard",
            #     support_email="mailto:support@finnovent.com",
            # )
            return {"status": "success", "message": response}
        else:
            return {"status": "error", "message": "unable to create account"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "email already exist"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login/")
async def login_user(form_data: UserLogin = Depends(), auth: Auth = Depends(get_auth),
                     db: Session = Depends(get_session_local)):
    users = auth.login_user(form_data.email, form_data.password, db)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"data": int(users.id), 'user_type': users.user_type}, expires_delta=access_token_expires
    )
    response_content = {"status": "success", "access_token": access_token}
    if users.user_type == 'customer':
        return response_content
    elif users.user_type == 'admin' or users.user_type == 'super_admin':
        return response_content
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized",
        )

# @router.post("/logout/")
# async def logout(response: Response):
#     response.set_cookie(key="access_token", value="", expires=0)
#     return {"message": "Logged out successfully"}
