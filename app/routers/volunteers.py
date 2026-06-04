from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ALL VOLUNTEERS
@router.get("/")
def get_volunteers(db: Session = Depends(get_db)):

    v = db.query(models.Volunteer).all()

    return {
        "volunteers": v
    }


# GET MENTEES FOR EACH VOLUNTEER
@router.get("/{volunteer_id}/mentees")
def get_mentees(volunteer_id: int, db: Session = Depends(get_db)):

    mentees = db.query(models.Mentee).filter(
        models.Mentee.volunteer_id == volunteer_id
    ).all()

    return {
        "mentees": mentees
    }