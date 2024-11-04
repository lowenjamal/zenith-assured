import os
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from models.user.user import User
from sqlalchemy.orm import Session
from mailer import mailer_func


def send_reset_email(subject, recipient: list, name, action_url, support_url):
    template_path = os.path.abspath("email_templates/reset_password.html")
    with open(template_path, "r") as file:
        html_content = file.read()
        html_content = html_content.replace("{{name}}", name)
        html_content = html_content.replace("{{action_url}}", action_url)
        html_content = html_content.replace("{{support_url}}", support_url)

        mailer_func.send_email(subject=subject, html_content=html_content, recipient=recipient)


def send_verification_email(subject, recipient: list, name, action_url, company_name):
    template_path = os.path.abspath("email_templates/verification_email.html")
    with open(template_path, "r") as file:
        html_content = file.read()
        html_content = html_content.replace("{{name}}", name)
        html_content = html_content.replace("{{action_url}}", action_url)
        html_content = html_content.replace("{{company_name}}", company_name)

        mailer_func.send_email(subject=subject, html_content=html_content, recipient=recipient)


class VerifyAndReset:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.secret_key = os.getenv("JWT_SECRET_TOKEN")
        self.algorithm = os.getenv("ALGORITHM")
        self.expires_at = 24
        self.url = os.getenv("FRONTEND_URL")
        self.credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def send_reset_password_email(self, email: str):
        response = {"status": "success"}
        user = self.db.query(User).filter(User.email == email).first()

        if user:
            user_data = {"id": user.id, "created_at": user.created_at.strftime("%Y-%m-%dT%H:%M:%SZ")}
            token = self.create_email_token(user_data)
            url = f"{self.url}/reset-password/?token={token}"
            recipient = [{
                "name": f"{user.first_name} {user.last_name}",
                "email": f"{email}"
            }]
            send_reset_email(
                subject=f"Email Reset for {recipient[0]['name']} ",
                recipient=recipient,
                name=f"{recipient[0]['name']}",
                action_url=url,
                support_url="#"
            )
        else:
            response = {"status": "error", "message": "email does not exist"}
        return response

    def reset_password(self, token, password: str):
        if token:
            try:
                data = jwt.decode(token, self.secret_key, self.algorithm)
                hashed_password = self.pwd_context.hash(password)
                user = self.db.query(User).filter(User.id == data['id']).first()
                if user:
                    user.password = hashed_password
                    self.db.commit()
                    self.db.refresh(user)
                    return {"status": "success", "message": "password reset successfully"}
            except JWTError:
                raise self.credentials_exception

    def verify_user(self, token):
        if token:
            try:
                data = jwt.decode(token, self.secret_key, self.algorithm)
                user = self.db.query(User).filter(User.id == data['id']).first()
                if user:
                    user.verified = True
                    self.db.commit()
                    self.db.refresh(user)
                    return {"status": "success", "message": "email verified successfully"}
            except JWTError:
                raise self.credentials_exception

    def send_verification_email(self, user_id: int):
        response = {"status": "success"}
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            if not user.verified:
                user_data = {"id": user.id, "created_at": user.verified}
                token = self.create_email_token(user_data)
                url = f"{self.url}/dashboard/verify-email/?token={token}"
                recipient = [{
                    "name": f"{user.first_name} {user.last_name}",
                    "email": f"{user.email}"
                }]
                send_verification_email(
                    subject=f"Email Reset for {recipient[0]['name']} ",
                    recipient=recipient,
                    name=f"{recipient[0]['name']}",
                    action_url=url,
                    company_name="Atlas Waves Team"
                )
            else:
                response = {"status": "error", "message": "user is already verified"}
            return response

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(hours=self.expires_at)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
