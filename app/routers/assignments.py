from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models
from ..auth import admin_required

router = APIRouter(prefix="/assign", tags=["Assignment"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ASSIGN MENTEE TO MENTOR
# =========================
@router.post("/")
def assign(
    mentor_id: int,
    mentee_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    mentor = db.query(models.User).filter_by(id=mentor_id, role="mentor").first()
    mentee = db.query(models.Mentee).filter_by(id=mentee_id).first()

    if not mentor:
        raise HTTPException(404, "Mentor not found")

    if not mentee:
        raise HTTPException(404, "Mentee not found")

    assignment = models.MentorMentee(
        mentor_id=mentor.id,
        mentee_id=mentee.id
    )

    db.add(assignment)
    db.commit()

    return {
        "success": True,
        "message": "Mentor assigned to mentee"
    }