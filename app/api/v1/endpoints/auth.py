from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schema import UserCreate, UserRead, Token
from app.services.user_service import create_user, authenticate_user, get_user_by_email
from app.utils.security import create_access_token
from app.utils.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await get_user_by_email(db, user.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(db, user.email, user.password)

@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_user = await authenticate_user(db, user.email, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(auth_user.id), "email": auth_user.email})
    return {"access_token": token, "token_type": "bearer"}