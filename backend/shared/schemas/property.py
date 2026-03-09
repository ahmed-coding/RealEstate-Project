"""
Shared Property Schemas
Pydantic models for cross-service communication
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal


class AddressSchema(BaseModel):
    """Address data schema"""
    id: int
    state: str
    city: str
    country: str
    longitude: float
    latitude: float
    line1: Optional[str] = ""
    line2: Optional[str] = ""

    class Config:
        from_attributes = True


class CategorySchema(BaseModel):
    """Category data schema"""
    id: int
    name: str
    parent_id: Optional[int] = None
    level: int = 0

    class Config:
        from_attributes = True


class ImageSchema(BaseModel):
    """Image data schema"""
    id: int
    url: str

    class Config:
        from_attributes = True


class FeatureSchema(BaseModel):
    """Feature data schema"""
    id: int
    name: str
    value: Optional[str] = None
    images: List[ImageSchema] = []

    class Config:
        from_attributes = True


class PropertyBase(BaseModel):
    """Base property schema"""
    name: str
    description: str
    price: Optional[Decimal] = None
    size: int
    is_active: bool = True
    for_sale: bool = False
    is_featured: bool = False
    for_rent: bool = False


class PropertySchema(PropertyBase):
    """Full property schema for cross-service communication"""
    id: int
    user_id: int
    category_id: int
    address: Optional[AddressSchema] = None
    unique_number: str
    image_urls: List[str] = []
    features: List[FeatureSchema] = []
    time_created: datetime
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


class PropertyListItem(BaseModel):
    """Lightweight property schema for listings"""
    id: int
    name: str
    price: Optional[Decimal] = None
    size: int
    image_urls: List[str] = []
    address: Optional[str] = None

    class Config:
        from_attributes = True


class PropertySearchFilters(BaseModel):
    """Property search filters"""
    query: Optional[str] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    category_id: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    for_sale: Optional[bool] = None
    for_rent: Optional[bool] = None
    is_featured: Optional[bool] = None


class PropertyCreateRequest(BaseModel):
    """Schema for creating a property"""
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    price: Optional[Decimal] = None
    size: int = Field(..., gt=0)
    category_id: int
    address_id: Optional[int] = None
    for_sale: bool = False
    for_rent: bool = False
    features: List[int] = []


class PropertyUpdateRequest(BaseModel):
    """Schema for updating a property"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    price: Optional[Decimal] = None
    size: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = None
    address_id: Optional[int] = None
    for_sale: Optional[bool] = None
    for_rent: Optional[bool] = None
    is_active: Optional[bool] = None
