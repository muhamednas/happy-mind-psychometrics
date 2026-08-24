import uuid
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class AssessmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: str
    time_limit_minutes: int = 30
    questions: List[Any] = []

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    questions: Optional[List[Any]] = None

class AssessmentResponse(AssessmentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
