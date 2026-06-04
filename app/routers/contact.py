from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import ContactMessage
from ..schemas import ContactCreate

router = APIRouter(
    prefix="/contact",
    tags=["Contact"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db)
):
    new_message = ContactMessage(
        name=contact.name,
        email=contact.email,
        message=contact.message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {
        "success": True,
        "message": "Message sent successfully."
    }


@router.get("/")
def get_messages(
    db: Session = Depends(get_db)
):
    messages = db.query(ContactMessage).all()

    return {
        "success": True,
        "count": len(messages),
        "messages": messages
    }