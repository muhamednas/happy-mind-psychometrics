from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel

class OrganizationBase(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#6366f1"
    quota: Optional[int] = 0
    used_quota: Optional[int] = 0

class OrganizationCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#6366f1"
    quota: Optional[int] = 0

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    quota: Optional[int] = None
    used_quota: Optional[int] = None

class OrganizationResponse(OrganizationBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
