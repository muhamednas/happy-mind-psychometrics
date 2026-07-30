import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class CandidateBase(BaseModel):
    full_name: str
    email: str

class CandidateCreate(CandidateBase):
    access_code: str

class CandidateLogin(BaseModel):
    email: str
    access_code: str

class CandidateResponse(CandidateBase):
    id: uuid.UUID
    package_id: uuid.UUID
    access_code: str
    logged_in_at: Optional[datetime] = None
    created_at: datetime
    token: Optional[str] = None
    
    package_title: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[str] = None
    score: Optional[str] = None
    
    class Config:
        from_attributes = True

class CandidateProgressResponse(BaseModel):
    id: uuid.UUID
    test_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    
    class Config:
        from_attributes = True
