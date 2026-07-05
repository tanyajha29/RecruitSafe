import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.user import User
from app.models.notification import Notification
from app.schemas.analysis import NotificationResponse
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
logger = logging.getLogger("recruitsafe")

@router.get("", response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
async def get_notifications(current_user: User = Depends(get_current_user)):
    """
    Retrieves all notifications for the authenticated user, sorted by creation date descending.
    """
    logger.info(f"Retrieving notifications for user: {current_user.email}")
    
    docs = await Notification.find(
        {"user_id": current_user.id}
    ).sort("-created_at").to_list()
    
    return [NotificationResponse.model_validate(doc) for doc in docs]

@router.put("/{notification_id}/read", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def mark_notification_read(notification_id: str, current_user: User = Depends(get_current_user)):
    """
    Marks a single notification as read.
    """
    logger.info(f"Marking notification {notification_id} as read for user {current_user.email}")
    
    try:
        notification = await Notification.get(notification_id)
    except Exception:
        notification = None

    if not notification or notification.user_id != current_user.id:
        logger.warning(f"Notification not found or unauthorized: {notification_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested notification was not found."
        )
        
    notification.is_read = True
    await notification.save()
    
    return NotificationResponse.model_validate(notification)

@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    """
    Marks all unread notifications for the user as read.
    """
    logger.info(f"Marking all notifications as read for user: {current_user.email}")
    
    await Notification.find({
        "user_id": current_user.id,
        "is_read": False
    }).update({"$set": {"is_read": True}})
    
    return {"message": "All notifications marked as read"}
