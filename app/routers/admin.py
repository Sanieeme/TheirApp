from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..security import hash_password
from ..auth import admin_required

router = APIRouter(prefix="/admin", tags=["Admin"])


# =====================================================
# DB SESSION
# =====================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# CREATE USER (ONLY ADMIN)
# =====================================================
@router.post("/create-user")
def create_user(
    data: schemas.UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    exists = db.query(models.User).filter(
        models.User.username == data.username
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    user = models.User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role  # mentor | tutor | volunteer
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "User created",
        "data": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }


# =====================================================
# ASSIGN MENTOR / TUTOR TO APPLICATION
# =====================================================
@router.post("/assign")
def assign(
    application_id: int,
    mentor_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    app = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    mentor = db.query(models.User).filter(
        models.User.id == mentor_id,
        models.User.role.in_(["mentor", "tutor"])
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor/Tutor not found")

    app.mentor_id = mentor.id
    app.status = "approved"

    db.commit()

    return {
        "success": True,
        "message": "Assigned successfully",
        "data": {
            "application_id": app.id,
            "mentor_id": mentor.id
        }
    }


# =====================================================
# VIEW USERS
# =====================================================
@router.get("/users")
def users(db: Session = Depends(get_db), admin=Depends(admin_required)):

    return {
        "success": True,
        "data": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role
            }
            for u in db.query(models.User).all()
        ]
    }


# =====================================================
# VIEW MENTORSHIPS
# =====================================================
@router.get("/mentorships")
def mentorships(db: Session = Depends(get_db), admin=Depends(admin_required)):

    apps = db.query(models.Application).filter(
        models.Application.mentor_id.isnot(None)
    ).all()

    return {
        "success": True,
        "data": [
            {
                "application_id": a.id,
                "student": a.name,
                "program": a.program,
                "mentor_id": a.mentor_id,
                "status": a.status
            }
            for a in apps
        ]
    }