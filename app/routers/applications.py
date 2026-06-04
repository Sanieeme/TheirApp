from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..auth import admin_required

router = APIRouter(prefix="/applications", tags=["Applications"])


# ========================
# DB
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
        raise HTTPException(400, "Invalid program")

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
        "data": {
            "id": new_app.id,
            "name": new_app.name,
            "program": new_app.program,
            "status": new_app.status
        }
    }


# ========================
# GET ALL (ADMIN)
# ========================
@router.get("/")
def get_applications(db: Session = Depends(get_db), admin=Depends(admin_required)):

    apps = db.query(models.Application).all()

    return {
        "success": True,
        "data": [
            {
                "id": a.id,
                "name": a.name,
                "email": a.email,
                "program": a.program,
                "status": a.status
            }
            for a in apps
        ]
    }


# ========================
# APPROVE
# ========================
@router.put("/{application_id}/approve")
def approve_application(
    application_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    app = db.query(models.Application).filter_by(id=application_id).first()

    if not app:
        raise HTTPException(404, "Application not found")

    app.status = "approved"
    app.assigned_admin_id = admin.id

    db.commit()

    return {
        "success": True,
        "message": f"{app.program} application approved"
    }


# ========================
# REJECT
# ========================
@router.put("/{application_id}/reject")
def reject_application(
    application_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):

    app = db.query(models.Application).filter_by(id=application_id).first()

    if not app:
        raise HTTPException(404, "Application not found")

    app.status = "rejected"
    app.assigned_admin_id = admin.id

    db.commit()

    return {
        "success": True,
        "message": "Application rejected"
    }


# ========================
# ANALYTICS
# ========================
@router.get("/analytics/overview")
def analytics(db: Session = Depends(get_db), admin=Depends(admin_required)):

    return {
        "success": True,
        "data": {
            "total": db.query(models.Application).count(),
            "approved": db.query(models.Application).filter_by(status="approved").count(),
            "rejected": db.query(models.Application).filter_by(status="rejected").count(),
            "pending": db.query(models.Application).filter_by(status="pending").count(),
        }
    }