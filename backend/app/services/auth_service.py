import logging
import secrets
import smtplib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bcrypt
import jwt

from app.config import settings

logger = logging.getLogger("recruitsafe")

def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using bcrypt.
    """
    pw_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error verifying password hash: {e}")
        return False

def create_access_token(user_id: str, email: str) -> str:
    """
    Generates a JWT access token containing user_id and email, set to expire in 24 hours.
    """
    now = datetime.utcnow()
    expire = now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": now
    }
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes a JWT access token. Returns the payload dictionary if valid, or None if expired/invalid.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token verification failed: Token signature expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None

def generate_reset_token() -> str:
    """
    Generates a cryptographically secure random url-safe token for password resets.
    """
    return secrets.token_urlsafe(32)

async def send_password_reset(email: str, token: str) -> None:
    """
    Delivers a password reset link to the target user.
    If SMTP credentials are provided, sends a secure email.
    Otherwise, logs the link in the developer terminal console as a fallback.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    smtp_configured = all([
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        settings.SMTP_USERNAME,
        settings.SMTP_PASSWORD
    ])
    
    if smtp_configured:
        try:
            logger.info(f"Sending password reset email to {email} via SMTP...")
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = email
            msg["Subject"] = "RecruitSafe Password Reset Request"
            
            body = f"""Hello,

You requested to reset your password on the RecruitSafe Platform. 
Please click the link below to set a new password. This reset link is valid for 1 hour.

{reset_url}

If you did not request this, please ignore this email.

Best regards,
The RecruitSafe Security Team
"""
            msg.attach(MIMEText(body, "plain"))
            
            # Send message securely
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, email, msg.as_string())
                
            logger.info(f"Password reset email sent to {email} successfully.")
        except Exception as e:
            logger.error(f"Failed to deliver reset email to {email}: {e}")
            # Print link as backup so development is not blocked
            print(f"\n[DEVELOPER FALLBACK] Password Reset URL for {email}:\n{reset_url}\n", flush=True)
    else:
        logger.info("SMTP configuration incomplete. Printing reset link to console.")
        # Flush print to display immediately in server terminal stdout
        print(f"\n[DEVELOPER FALLBACK] Password Reset URL for {email}:\n{reset_url}\n", flush=True)
