import uuid
from typing import Dict, Any
from pydantic import BaseModel


class ResponseSave(BaseModel):
    assessment_id: uuid.UUID
    question_id: str
    response: Dict[str, Any]


class ResponseSubmit(BaseModel):
    pass
