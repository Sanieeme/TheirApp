from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin | mentor | tutor | volunteer

    # Relationship to applications they manage
    applications = relationship("Application", back_populates="mentor")
    
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    program = Column(String, nullable=False)
    message = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # FIXED RELATIONSHIP
    mentor = relationship("User", back_populates="applications")
    
    
class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
# VOLUNTEERS (NEW FEATURE)
class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    role = Column(String)   # mentoring / tutoring / career guidance
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    
# -------------------------
# MENTEES (ASSIGNED TO VOLUNTEERS)
# -------------------------
class Mentee(Base):
    __tablename__ = "mentees"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String)

    volunteer_id = Column(Integer, ForeignKey("volunteers.id"))
    
class MentorMentee(Base):
    __tablename__ = "mentor_mentees"

    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    mentee_name = Column(String)
    mentee_email = Column(String)