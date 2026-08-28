import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CorporateBase(BaseModel):
    name: str
    slug: str


class CorporateCreate(CorporateBase):
    pass


class CorporateResponse(CorporateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
