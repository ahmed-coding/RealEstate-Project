"""
Shared User Schemas
Pydantic models for cross-service communication
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: Optional[str] = ""
    username: Optional[str] = None
    phone_number: Optional[str] = None
    user_type: str = "customer"


class UserSchema(UserBase):
    """Full user schema for cross-service communication"""
    id: int
    is_active: bool = True
    is_seller: bool = False
    is_staff: bool = False
    date_joined: datetime
    profile_image_url: Optional[str] = None
    unique_no: str

    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """Public user profile schema (limited fields)"""
    id: int
    name: str
    username: Optional[str] = None
    profile_image_url: Optional[str] = None
    user_type: str

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=60)
    username: Optional[str] = None
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    user_type: str = "customer"


class UserUpdateRequest(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=60)
    username: Optional[str] = None
    phone_number: Optional[str] = None
    image: Optional[str] = None


class UserPreferences(BaseModel):
    """User preferences for recommendations"""
    user_id: int
    preferred_categories: List[int] = []
    preferred_cities: List[str] = []
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    preferred_property_types: List[str] = []
    favorite_features: List[str] = []
    search_history: List[str] = []


class UserSearchHistory(BaseModel):
    """User search history for recommendations"""
    id: int
    user_id: int
    query: str
    filters: dict = {}
    timestamp: datetime

    class Config:
        from_attributes = True
