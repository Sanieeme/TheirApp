from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models
from ..auth import admin_required

router = APIRouter(prefix="/schools", tags=["Schools"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================
# ADD SCHOOL
# ========================
@router.post("/")
def add_school(data: dict, db: Session = Depends(get_db), admin=Depends(admin_required)):

    school = models.School(name=data["name"])

    db.add(school)
    db.commit()
    db.refresh(school)

    return {"success": True, "data": school}


# ========================
# GET ALL SCHOOLS
# ========================
@router.get("/")
def get_schools(db: Session = Depends(get_db), admin=Depends(admin_required)):

    schools = db.query(models.School).all()

    return {"success": True, "data": schools}