from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..auth import admin_required
from ..schemas import MenteeCreate

router = APIRouter(prefix="/mentees", tags=["Mentees"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ADD MENTEE (ADMIN ONLY)
# =========================
@router.post("/")
# def add_mentee(
#     data: schemas.MenteeCreate,
#     db: Session = Depends(get_db),
#     admin=Depends(admin_required)
# ):

@router.post("/")
def add_mentee(
    data: schemas.MenteeCreate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    school = db.query(models.School).filter_by(id=data.school_id).first()

    if not school:
        raise HTTPException(404, "School not found")

    mentee = models.Mentee(
        name=data.name,
        email=data.email,
        phone=data.phone,
        school_id=data.school_id
    )

    db.add(mentee)
    db.commit()
    db.refresh(mentee)

    return {"success": True, "data": mentee}


# =========================
# GET BY SCHOOL
# =========================
@router.get("/school/{school}")
def get_by_school(school: str, db: Session = Depends(get_db), admin=Depends(admin_required)):

    mentees = db.query(models.Mentee).filter(models.Mentee.school == school).all()

    return {"success": True, "data": mentees}


@router.get("/schools/{school_id}/mentees")
def school_mentees(
    school_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    mentees = db.query(models.Mentee).filter(
        models.Mentee.school_id == school_id
    ).all()

    return {
        "success": True,
        "data": mentees
    }


# =========================
# ASSIGN MENTEES TO MENTOR
# =========================
@router.put("/assign")
def assign_mentees(payload: dict, db: Session = Depends(get_db), admin=Depends(admin_required)):

    mentor_id = payload["mentor_id"]
    mentee_ids = payload["mentee_ids"]

    mentor = db.query(models.User).filter_by(id=mentor_id, role="mentor").first()

    if not mentor:
        raise HTTPException(404, "Mentor not found")

    mentees = db.query(models.Mentee).filter(models.Mentee.id.in_(mentee_ids)).all()

    for m in mentees:
        exists = db.query(models.Assignment).filter(
            models.Assignment.mentor_id == mentor_id,
            models.Assignment.mentee_id == m.id
        ).first()

        if not exists:

            assignment = models.Assignment(
                mentor_id=mentor_id,
                mentee_id=m.id
            )

            db.add(assignment)
            db.commit()

    return {
        "success": True,
        "message": "Mentees assigned to mentor"
    }


# =========================
# GET MENTOR WITH MENTEES
# =========================
@router.get("/mentor/{mentor_id}")
def mentor_detail(mentor_id: int, db: Session = Depends(get_db)):

    mentor = db.query(models.User).filter_by(id=mentor_id).first()

    if not mentor:
        raise HTTPException(404, "Mentor not found")

    assignments = db.query(models.Assignment).filter(
        models.Assignment.mentor_id == mentor_id
    ).all()

    return {
        "mentor": mentor.username,
        "mentees": [
            {
                "id": a.mentee.id,
                "name": a.mentee.name,
                "email": a.mentee.email
            }
            for a in assignments
        ]
    }
    

@router.get("/mentors")
def get_mentors(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    mentors = db.query(models.User).filter(
        models.User.role == "mentor"
    ).all()

    return {
        "success": True,
        "data": mentors
    }
    
@router.get("/mentor/{mentor_id}/assignments")
def mentor_assignments(
    mentor_id: int,
    db: Session = Depends(get_db)
):

    assignments = db.query(models.Assignment).filter(
        models.Assignment.mentor_id == mentor_id
    ).all()

    return {
        "success": True,
        "data": [
            {
                "name": a.mentee.name,
                "email": a.mentee.email,
                "grade": a.mentee.grade,
                "school": a.mentee.school.name
            }
            for a in assignments
        ]
    }