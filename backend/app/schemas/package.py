import uuid
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class PackageBase(BaseModel):
    title: str
    description: Optional[str] = None
    tests: List[Any]

class PackageCreate(PackageBase):
    organization_name: str

class PackageResponse(PackageBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    access_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    candidate_count: Optional[int] = None
    
    class Config:
        from_attributes = True
