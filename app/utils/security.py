from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import hashlib
from app.config import settings
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def get_password_hash(password: str):
    raw = password.encode("utf-8")
    return pwd_context.hash(password)

def generate_verification_code():
    """Return a random 6-digit OTP code as string."""
    return str(random.randint(100000, 999999))

def send_verification_email(recipient_email: str, code: str, subject: str = "Your Verification Code"):
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    smtp_username = settings.SMTP_USERNAME
    smtp_password = settings.SMTP_PASSWORD
    sender_email = settings.SENDER_EMAIL

    if not all([smtp_server, smtp_port, smtp_username, smtp_password, sender_email]):
        raise ValueError("SMTP credentials are not fully set in environment variables.")

    body = f"Your verification code is: {code}\n\nThis code is only valid for 2 minutes."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
    except Exception as e:
        raise RuntimeError(f"Failed to send email: {e}")

def send_otp(recipient_email: str, purpose: str = "login") -> str:
    """Generate a 6-digit OTP and email it. Returns the OTP string."""
    code = generate_verification_code()
    subject = f"Your {purpose.capitalize()} Code"
    send_verification_email(recipient_email, code, subject)
    return code
    
def verify_password(plain: str, hashed: str):
    raw = plain.encode("utf-8")
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)