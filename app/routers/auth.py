from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..security import verify_password
from ..auth import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def login(
    data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.username == data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid username"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid password"
        )

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }