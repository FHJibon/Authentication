from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import hashlib
from app.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def get_password_hash(password: str):
    raw = password.encode("utf-8")
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    raw = plain.encode("utf-8")
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)