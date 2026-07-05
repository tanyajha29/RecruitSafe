from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    TokenResponse,
    UserResponse
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    generate_reset_token,
    send_password_reset
)
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger("recruitsafe")

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    """
    Creates a new user account.
    Verifies that the email is unique, hashes the password using bcrypt,
    registers the user in MongoDB, and issues a 24-hour JWT token.
    """
    # Check for duplicate email
    existing_user = await User.find_one({"email": payload.email})
    if existing_user:
        logger.warning(f"Registration failed: Email {payload.email} is already registered.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Hash the password
    pw_hash = hash_password(payload.password)
    
    # Save the user document
    new_user = User(
        email=payload.email,
        password_hash=pw_hash,
        full_name=payload.full_name,
        last_login=datetime.utcnow()
    )
    await new_user.insert()
    logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")

    # Issue access token
    token = create_access_token(user_id=str(new_user.id), email=new_user.email)
    
    user_res = UserResponse.model_validate(new_user)
    return TokenResponse(access_token=token, user=user_res)

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest):
    """
    Logs in an existing user.
    Validates email/password credentials against the database and returns a JWT access token.
    """
    user = await User.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning(f"Login failed: Invalid credentials for {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        logger.warning(f"Login failed: User account {payload.email} is deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your user account has been deactivated."
        )

    # Update last login time
    user.last_login = datetime.utcnow()
    await user.save()
    logger.info(f"User logged in successfully: {user.email}")

    # Generate token
    token = create_access_token(user_id=str(user.id), email=user.email)
    
    user_res = UserResponse.model_validate(user)
    return TokenResponse(access_token=token, user=user_res)

@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(payload: PasswordResetRequest):
    """
    Initiates password reset.
    Generates a secure reset token, links it to the user in MongoDB with a 1-hour expiration,
    and calls the email service (which falls back to console printing in dev mode).
    """
    user = await User.find_one({"email": payload.email})
    if not user:
        logger.warning(f"Password reset request failed: User with email {payload.email} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address."
        )

    # Generate reset token
    token = generate_reset_token()
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    # Store token in database
    reset_entry = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expiry
    )
    await reset_entry.insert()
    
    # Deliver reset token (SMTP or console log)
    await send_password_reset(email=user.email, token=token)
    
    return {"message": "Reset email sent"}

@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(payload: PasswordResetConfirm):
    """
    Confirms password reset.
    Verifies the reset token exists, is unexpired, and hasn't been used yet.
    Updates the password hash and invalidates the token.
    """
    # Find active token
    reset_token = await PasswordResetToken.find_one(
        {"token": payload.token}
    )
    
    if not reset_token or reset_token.used or reset_token.expires_at < datetime.utcnow():
        logger.warning(f"Password reset confirmation failed: Invalid, expired, or used token.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password reset link is invalid or has expired."
        )
        
    user = await User.get(reset_token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user account not found."
        )
        
    # Hash and save the new password
    pw_hash = hash_password(payload.new_password)
    user.password_hash = pw_hash
    user.updated_at = datetime.utcnow()
    await user.save()
    
    # Mark token as used
    reset_token.used = True
    await reset_token.save()
    
    logger.info(f"Password reset successfully for user: {user.email}")
    return {"message": "Password updated"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logs out the current authenticated user (client handles token discard).
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Logged out"}
