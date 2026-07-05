import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.schemas.user import UserResponse, ProfileUpdateRequest, PasswordChangeRequest
from app.middleware.auth import get_current_user
from app.services.auth_service import hash_password, verify_password

router = APIRouter(prefix="/api/profile", tags=["Profile"])
logger = logging.getLogger("recruitsafe")

@router.get("", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieves the current authenticated user's profile details.
    """
    logger.info(f"Fetching profile details for: {current_user.email}")
    return UserResponse.model_validate(current_user)

@router.put("", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_profile(payload: ProfileUpdateRequest, current_user: User = Depends(get_current_user)):
    """
    Updates the current user's profile details.
    Validates email uniqueness if a new email address is provided.
    """
    logger.info(f"Profile update requested for user: {current_user.email}")
    
    updated = False
    
    if payload.full_name is not None and payload.full_name.strip() != "":
        current_user.full_name = payload.full_name.strip()
        updated = True
        
    if payload.email is not None and payload.email.lower().strip() != current_user.email:
        new_email = payload.email.lower().strip()
        # Verify email is unique
        existing_user = await User.find_one({"email": new_email})
        if existing_user:
            logger.warning(f"Profile update rejected: Email {new_email} is already registered by another user.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email address is already in use by another account."
            )
        current_user.email = new_email
        updated = True
        
    if updated:
        current_user.updated_at = datetime.utcnow()
        await current_user.save()
        logger.info(f"Profile updated successfully for: {current_user.email}")
    else:
        logger.info(f"No profile changes made for: {current_user.email}")
        
    return UserResponse.model_validate(current_user)

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(payload: PasswordChangeRequest, current_user: User = Depends(get_current_user)):
    """
    Changes the user's password.
    Requires and validates the current password before applying the new bcrypt hash.
    """
    logger.info(f"Password change requested for user: {current_user.email}")
    
    # Verify current password
    if not verify_password(payload.current_password, current_user.password_hash):
        logger.warning(f"Password change failed: Incorrect current password for {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The current password you entered is incorrect."
        )
        
    # Check that the new password is not identical to current
    if verify_password(payload.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your new password cannot be the same as your current password."
        )
        
    # Hash and save new password
    new_hash = hash_password(payload.new_password)
    current_user.password_hash = new_hash
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    logger.info(f"Password updated successfully for user: {current_user.email}")
    return {"message": "Password changed"}
