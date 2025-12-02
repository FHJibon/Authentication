from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.model.model import User
from app.utils.security import get_password_hash, verify_password, send_otp
from datetime import datetime, timedelta

_pending_signup: dict[str, tuple[str, str, datetime]] = {}

def _now():
    return datetime.utcnow()

def _expiry(minutes: int = 5):
    return _now() + timedelta(minutes=minutes)

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, email: str, password: str):
    try:
        hashed_password = get_password_hash(password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Password hashing error: {str(e)}")
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

    

async def start_signup(email: str, password: str) -> None:
    hashed = get_password_hash(password)
    code = send_otp(email, "signup")
    _pending_signup[email] = (hashed, code, _expiry())

async def verify_signup(db: AsyncSession, email: str, code: str):
    item = _pending_signup.get(email)
    if not item:
        return False
    hashed_password, stored_code, expires_at = item
    if _now() > expires_at:
        _pending_signup.pop(email, None)
        return False
    if stored_code != code:
        return False
    user = await get_user_by_email(db, email)
    if user:
        _pending_signup.pop(email, None)
        return False
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    _pending_signup.pop(email, None)
    return new_user