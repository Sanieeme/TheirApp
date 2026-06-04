from pydantic import BaseModel, EmailStr
from typing import Optional


# ==========================================
# APPLICATIONS
# ==========================================

class ApplicationCreate(BaseModel):
    name: str
    email: EmailStr
    program: str
    message: Optional[str] = None


class ApplicationResponse(ApplicationCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


# ==========================================
# CONTACT FORM
# ==========================================

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    message: str


class ContactResponse(ContactCreate):
    id: int

    class Config:
        from_attributes = True


# ==========================================
# ADMIN LOGIN
# ==========================================

class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==========================================
# VOLUNTEERS
# ==========================================

class VolunteerCreate(BaseModel):
    name: str
    email: EmailStr
    role: str


class VolunteerResponse(VolunteerCreate):
    id: int

    class Config:
        from_attributes = True
        
class LoginRequest(BaseModel):
    username: str
    password: str