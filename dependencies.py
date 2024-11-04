from jose import JWTError, jwt
from fastapi import HTTPException, status, Request, Depends, Header
from models.user.user import User
from sqlalchemy.orm import Session
from database import SessionLocal

SECRET_KEY = "6b1e54bb86c5c43c8fce2a9a8823c24919bf76d24434b66f197b19d2822166d9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_token_header(x_token: str = Header(...)):
    if x_token:
        try:
            payload = jwt.decode(x_token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise credentials_exception
    else:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "X-Token header invalid"})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def check_if_user_admin(x_token: str = Header(...), db: Session = Depends(get_db)):
    if x_token:
        try:
            payload = jwt.decode(x_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get('data', None)
            if user_id is None:
                raise HTTPException(status_code=404, detail="User not found")
            user = db.query(User).filter(User.id == user_id).first()
            if user.user_type not in ('admin', 'super_admin'):
                raise HTTPException(status_code=403, detail="User is not an admin or super admin")
            return user_id
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    else:
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def check_if_super_admin(x_token: str = Header(...), db: Session = Depends(get_db)):
    if x_token:
        try:
            payload = jwt.decode(x_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get('data', None)
            if user_id is None:
                raise HTTPException(status_code=404, detail="User not found")
            user = db.query(User).filter(User.id == user_id).first()
            if user.user_type != 'super_admin':
                raise HTTPException(status_code=403, detail="User is not super admin")
            return user_id
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    else:
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def can_use_route(x_token: str = Header(...)):
    if x_token:
        try:
            if x_token != "hi8qX8qLpJmCYQX5eL7Ifz47CpOtxf2EpyxxGh7MItghqs34mo":
                raise HTTPException(status_code=401, detail="Invalid Header Used.")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    else:
        raise HTTPException(status_code=400, detail="X-Token header empty")



