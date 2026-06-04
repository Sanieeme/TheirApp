from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..auth import admin_required

router = APIRouter(prefix="/applications", tags=["Applications"])


# ========================
# DB SESSION
# ========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================
# CREATE APPLICATION
# ========================
@router.post("/")
def create_application(app: schemas.ApplicationCreate, db: Session = Depends(get_db)):

    valid_programs = ["mentor", "tutor", "career_guidance"]

    if app.program not in valid_programs:
        raise HTTPException(status_code=400, detail="Invalid program")

    new_app = models.Application(
        name=app.name,
        email=app.email,
        program=app.program,
        message=app.message,
        status="pending"
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    return {
        "success": True,
        "message": "Application submitted successfully",
        "data": new_app
    }


# ========================
# GET ALL APPLICATIONS
# ========================
@router.get("/")
def get_applications(db: Session = Depends(get_db), admin=Depends(admin_required)):

    apps = db.query(models.Application).all()

    return {
        "success": True,
        "data": apps
    }


# ========================
# APPROVE APPLICATION
# ========================
@router.put("/{application_id}/approve")
def approve_application(application_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):

    app = db.query(models.Application).filter_by(id=application_id).first()

    if not app:
        raise HTTPException(404, "Application not found")

    app.status = "approved"
    app.assigned_admin_id = admin.id

    # ONLY create mentor if program is mentor
    if app.program == "mentor":
        user = db.query(models.User).filter_by(username=app.email).first()
        if not user:
            user = models.User(
                username=app.email,
                password_hash="TEMP", # Remember to update this to a safe hashed value later!
                role="mentor"
            )
            db.add(user)

    db.commit()

    return {
        "success": True,
        "message": "Application approved"
    }


# ========================
# REJECT APPLICATION
# ========================
@router.put("/{application_id}/reject")
def reject_application(
    application_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    app = db.query(models.Application).filter_by(id=application_id).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = "rejected"
    db.commit()

    return {
        "success": True,
        "message": "Application rejected"
    }


# ========================
# GET ALL MENTORS (FIXED)
# ========================
# ========================
# GET ALL MENTORS (FIXED PATH AND PROTECTED)
# ========================
@router.get("/mentors")
def get_mentors(db: Session = Depends(get_db), admin=Depends(admin_required)): # Added admin check

    mentors = db.query(models.User).filter(
        models.User.role == "mentor"
    ).all()

    return {
        "success": True,
        "data": [
            {
                "id": m.id,
                "username": m.username
            }
            for m in mentors
        ]
    }

# ========================
# GET MENTOR + MENTEES
# ========================
# =====================================================
# GET MENTOR + MENTEES (FIXED DATA PAYLOAD STRUCTURE)
# =====================================================
# =====================================================
# GET MENTOR + MENTEES (FAILPROOF STRUCTURAL FIX)
# =====================================================
@router.get("/mentor/{mentor_id}")
def get_mentor_mentees(mentor_id: int, db: Session = Depends(get_db)):
    # 1. Grab all raw assignment entries for this mentor
    assignments = db.query(models.Assignment).filter_by(mentor_id=mentor_id).all()
    
    # 2. Extract just the mentee IDs out into a clean list
    mentee_ids = [a.mentee_id for a in assignments]
    
    # 3. Pull those specific mentees directly out of the Mentee table
    mentees = db.query(models.Mentee).filter(models.Mentee.id.in_(mentee_ids)).all()

    # 4. Return the data payload cleanly back to the front-end
    return {
        "success": True,
        "data": [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                # Resolve school string safely without relationship models
                "school": db.query(models.School).filter_by(id=m.school_id).first().name if m.school_id else "No School"
            }
            for m in mentees
        ]
    }


# ==========================================================
# GET ALL MENTEES WITH THEIR ASSIGNED MENTORS
# ==========================================================
# ==========================================================
# GET ALL MENTEES WITH DETAILED STATUS (FOR TABLE)
# ==========================================================
@router.get("/mentees-with-mentors")
def get_all_mentees_with_mentors(db: Session = Depends(get_db)):
    mentees = db.query(models.Mentee).all()
    result = []
    
    for m in mentees:
        assignment = db.query(models.Assignment).filter_by(mentee_id=m.id).first()
        
        has_mentor = assignment is not None and assignment.mentor is not None
        mentor_name = assignment.mentor.username if has_mentor else "Unassigned"
        
        result.append({
            "mentee_id": m.id,
            "name": m.name,
            "email": m.email,
            "phone": m.phone if hasattr(m, 'phone') else "N/A",
            "grade": m.grade if hasattr(m, 'grade') else "N/A",
            "school": m.school.name if m.school else "No School",
            "assigned_mentor": mentor_name,
            "is_assigned": has_mentor  # Useful for our frontend table filters
        })
        
    return {"success": True, "data": result}

# ========================
# ASSIGN MENTEES TO MENTOR
# ========================
@router.post("/assign")
def assign(data: dict, db: Session = Depends(get_db)):

    mentor_id = data["mentor_id"]
    mentee_ids = data["mentee_ids"]

    mentor = db.query(models.User).filter_by(id=mentor_id, role="mentor").first()

    if not mentor:
        raise HTTPException(404, "Mentor not found")

    for m_id in mentee_ids:
        exists = db.query(models.Assignment).filter_by(
            mentor_id=mentor_id,
            mentee_id=m_id
        ).first()

        if not exists:
            db.add(models.Assignment(
                mentor_id=mentor_id,
                mentee_id=m_id
            ))

    db.commit()

    return {"success": True}


@router.put("/../mentees/assign") 
def assign(data: dict, db: Session = Depends(get_db)):
    """
    Handles PUT http://127.0.0.1:8000/mentees/assign
    Expected JSON body payload: {"mentor_id": 1, "mentee_ids": [2]}
    """
    mentor_id = data.get("mentor_id")
    mentee_ids = data.get("mentee_ids", [])

    if not mentor_id or not mentee_ids:
        raise HTTPException(status_code=400, detail="Missing mentor_id or mentee_ids")

    # Verify the mentor exists and is actually assigned a mentor role profile
    mentor = db.query(models.User).filter_by(id=mentor_id, role="mentor").first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Selected Mentor not found")

    # Loop through and process matching assignments
    for m_id in mentee_ids:
        exists = db.query(models.Assignment).filter_by(
            mentor_id=mentor_id,
            mentee_id=m_id
        ).first()

        if not exists:
            db.add(models.Assignment(
                mentor_id=mentor_id,
                mentee_id=m_id
            ))

    db.commit()
    return {"success": True, "message": "Mentees assigned successfully"}


# ========================
# SCHOOLS
# ========================
@router.post("/schools")
def create_school(
    data: dict,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    school = models.School(name=data["name"])

    db.add(school)
    db.commit()
    db.refresh(school)

    return {
        "success": True,
        "data": school
    }


@router.get("/schools")
def get_schools(db: Session = Depends(get_db)):

    return {
        "success": True,
        "data": db.query(models.School).all()
    }


# ========================
# ADD MENTEE
# ========================
# ========================
# ADD MENTEE (UPDATED)
# ========================
@router.post("/mentees")
def add_mentee(
    data: dict,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    school = db.query(models.School).filter_by(id=data["school_id"]).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    # ✅ Read the new fields safely out of the dictionary pack
    mentee = models.Mentee(
        name=data["name"],
        email=data["email"],
        school_id=data["school_id"],
        grade=data.get("grade"),  # .get() prevents crashes if the field is empty
        phone=data.get("phone"),
        gender=data.get("gender")
    )

    db.add(mentee)
    db.commit()
    db.refresh(mentee)

    return {
        "success": True,
        "data": mentee
    }

# ========================
# ANALYTICS
# ========================
@router.get("/analytics/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    return {
        "success": True,
        "data": {
            "total": db.query(models.Application).count(),
            "approved": db.query(models.Application).filter_by(status="approved").count(),
            "rejected": db.query(models.Application).filter_by(status="rejected").count(),
            "pending": db.query(models.Application).filter_by(status="pending").count()
        }
    }