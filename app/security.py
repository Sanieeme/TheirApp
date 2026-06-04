from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# -------------------------------------------------
# FIX: protect bcrypt 72-byte limit
# -------------------------------------------------
def hash_password(password: str):
    if len(password) > 72:
        password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    if len(plain) > 72:
        plain = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(plain, hashed)