from pydantic import BaseModel
from typing import List, Optional
from app.models.models import ShortlistCategory

class ShortlistResponse(BaseModel):
    university_id: int
    university_name: str
    country: str
    category: ShortlistCategory
    locked: bool

class FinalizeStatus(BaseModel):
    shortlists: List[ShortlistResponse]
    locked_count: int
    can_proceed: bool

class LockRequest(BaseModel):
    university_id: int
