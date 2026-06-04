from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import applications, contact
from datetime import datetime
from .routers import auth, admin, applications
from app.routers import mentees
from app.routers import schools

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bono Foundation API")
app.include_router(auth.router)

# Allow frontend (GitHub Pages) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # later lock to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(applications.router)
app.include_router(contact.router)
app.include_router(mentees.router)
app.include_router(schools.router)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Welcome to Bono Foundation API 🚀",
        "description": "This API powers the Bono Foundation platform for applications, mentoring, tutoring, and contact services.",
        "version": "1.0.0",
        "organization": "Bono Foundation",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "endpoints": {
            "applications": "/applications/",
            "contact": "/contact/"
        }
    }