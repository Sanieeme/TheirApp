from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models
from ..auth import admin_required

router = APIRouter(prefix="/admin", tags=["Admin Assignment"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ASSIGN MENTEE TO MENTOR
# =========================
@router.post("/assign")
def assign_mentee(
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
        mentor_id=mentor_id,
        mentee_id=mentee_id
    )

    db.add(assignment)
    db.commit()

    return {
        "success": True,
        "message": "Mentee assigned to mentor"
    }


# =========================
# GET MENTOR MENTEES
# =========================
@router.get("/mentor/{mentor_id}")
def get_mentor_mentees(
    mentor_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    assignments = db.query(models.MentorMentee).filter_by(
        mentor_id=mentor_id
    ).all()

    return {
        "success": True,
        "data": [
            {
                "mentee_name": a.mentee.name,
                "school": a.mentee.school.name,
                "grade": a.mentee.grade
            }
            for a in assignments
        ]
    }