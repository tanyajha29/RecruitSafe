from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.models.user import User
from app.services.auth_service import decode_access_token
from beanie import PydanticObjectId

# Bearer security configuration
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

GUEST_USER_ID = PydanticObjectId("000000000000000000000000")

async def get_or_create_guest_user() -> User:
    guest = await User.get(GUEST_USER_ID)
    if not guest:
        guest = User(
            id=GUEST_USER_ID,
            email="guest@recruitsafe.local",
            password_hash="N/A",
            full_name="Guest User",
            is_active=True
        )
        await guest.save()
    return guest

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency injection handler to guard routes. Decodes the Bearer token,
    validates signature/expiry, fetches the associated User document,
    and returns the User model.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature has expired or token is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: user_id missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your user account has been deactivated."
        )
        
    return user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)) -> User:
    if not credentials:
        return await get_or_create_guest_user()
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        if not payload:
            return await get_or_create_guest_user()
        user_id = payload.get("user_id")
        if not user_id:
            return await get_or_create_guest_user()
        user = await User.get(user_id)
        if not user or not user.is_active:
            return await get_or_create_guest_user()
        return user
    except Exception:
        return await get_or_create_guest_user()

