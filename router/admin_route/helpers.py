from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt

# to get random secret key:
# openssl rand -hex 32
SECRET_KEY = "6b1e54bb86c5c43c8fce2a9a8823c24919bf76d24434b66f197b19d2822166d9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
