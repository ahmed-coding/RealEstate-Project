"""
Shared Chat Schemas
Pydantic models for cross-service communication
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    content: str


class ChatMessageSchema(ChatMessageBase):
    """Full chat message schema"""
    id: int
    room_id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    room_id: int


class ChatRoomBase(BaseModel):
    """Base chat room schema"""
    pass


class ChatRoomSchema(ChatRoomBase):
    """Full chat room schema"""
    id: int
    user1_id: int
    user2_id: int
    is_active: bool
    connected_users: List[int] = []

    class Config:
        from_attributes = True


class ChatRoomCreate(BaseModel):
    """Schema for creating a chat room"""
    user2_id: int


class UnreadMessageSchema(BaseModel):
    """Unread messages schema"""
    id: int
    room_id: int
    user_id: int
    count: int
    most_recent_message: Optional[str] = None
    reset_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str  # join, leave, message, typing, etc.
    room_id: Optional[int] = None
    user_id: Optional[int] = None
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: dict = {}


class ChatEvent(BaseModel):
    """Chat event for WebSocket broadcasting"""
    event_type: str  # chat.join, chat.leave, chat.message
    room_id: int
    user_id: int
    username: str
    profile_image: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = datetime.now()
