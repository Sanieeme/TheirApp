from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing = db.query(User).filter_by(username="admin").first()

if not existing:
    admin = User(
        username="admin",
        password_hash=hash_password("1234"),
        role="admin"
    )

    db.add(admin)
    db.commit()
    print("✅ Admin created!")
else:
    print("✅ Admin already exists")