import uuid
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AssessmentIn(BaseModel):
    title: str
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    questions: List[Any] = Field(default_factory=list)


class AssessmentResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    position: int
    questions: List[Any]

    model_config = ConfigDict(from_attributes=True)


class PackageBase(BaseModel):
    title: str
    description: Optional[str] = None


class PackageCreate(PackageBase):
    # Transitional: the corporate is derived from the authenticated HR user once
    # admin CRUD moves to supabase-js (Phase 4). Kept for the interim REST path.
    organization_name: str
    tests: List[AssessmentIn] = Field(default_factory=list)


class PackageResponse(PackageBase):
    id: uuid.UUID
    corporate_id: uuid.UUID
    access_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    candidate_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
