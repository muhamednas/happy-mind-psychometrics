from typing import Dict, Any
from pydantic import BaseModel

class ResponseSave(BaseModel):
    test_id: str
    question_id: str
    response: Dict[str, Any]

class ResponseSubmit(BaseModel):
    pass
