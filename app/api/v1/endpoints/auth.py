from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schema import UserCreate, UserRead, Token, VerifyOTPRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.services.user_service import authenticate_user, get_user_by_email, start_signup, verify_signup, start_password_reset, reset_password
from app.utils.security import create_access_token
from app.utils.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await get_user_by_email(db, user.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    await start_signup(user.email, user.password)
    return {"message": f"OTP has been sent to {user.email}. Please verify to complete account creation."}

@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_user = await authenticate_user(db, user.email, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(auth_user.id), "email": auth_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/verify")
async def verify_signup_endpoint(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    user = await verify_signup(db, payload.email, payload.code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"message": "Your account has been created. Please log in."}

@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    # Do not reveal whether the email exists
    await start_password_reset(payload.email)
    return {"message": "If an account exists for this email, a reset code has been sent."}

@router.post("/reset-password")
async def reset_password_endpoint(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    ok = await reset_password(db, payload.email, payload.code, payload.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    return {"message": "Your password has been reset successfully."}