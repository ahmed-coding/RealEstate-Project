"""
Shared Notification Schemas
Pydantic models for cross-service communication
"""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    """Base notification schema"""
    verb: str
    target_user_id: int
    from_user_id: Optional[int] = None
    read: bool = False


class NotificationSchema(NotificationBase):
    """Full notification schema"""
    id: int
    content_type: str
    object_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    verb: str
    target_user_id: int
    from_user_id: Optional[int] = None
    content_type: Optional[str] = None
    object_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    read: Optional[bool] = None


class NotificationPayload(BaseModel):
    """WebSocket notification payload"""
    id: int
    verb: str
    from_user_id: Optional[int] = None
    from_user_name: Optional[str] = None
    from_user_image: Optional[str] = None
    content_type: Optional[str] = None
    object_id: Optional[int] = None
    timestamp: datetime
    read: bool = False


class NotificationListResponse(BaseModel):
    """Response schema for notification list"""
    notifications: list[NotificationSchema]
    total_count: int
    unread_count: int
    page: int
    page_size: int
