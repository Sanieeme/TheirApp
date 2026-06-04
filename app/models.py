from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from .database import Base
from sqlalchemy.orm import relationship


# =========================
# USERS (Admin, Mentor, Tutor)
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String)

    assignments = relationship("Assignment", back_populates="mentor")

# =========================
# APPLICATIONS
# =========================
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    program = Column(String, nullable=False)
    message = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)


# =========================
# SCHOOLS
# =========================
class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    mentees = relationship("Mentee", back_populates="school")
    
    
# =========================
# MENTEES
# =========================
class Mentee(Base):
    __tablename__ = "mentees"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    grade = Column(String)

    school_id = Column(Integer, ForeignKey("schools.id"))

    school = relationship(
        "School",
        back_populates="mentees"
    )

# =========================
# ASSIGNMENT TABLE (CORE FIX)
# =========================

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)

    mentor_id = Column(Integer, ForeignKey("users.id"))
    mentee_id = Column(Integer, ForeignKey("mentees.id"))

    mentor = relationship("User", back_populates="assignments")
    mentee = relationship("Mentee")
    

# =========================
# CONTACT
# =========================
class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)