from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_SECRET"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

bearer_scheme = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# FIXED ADMIN CHECK
# =========================
def admin_required(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin only")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")