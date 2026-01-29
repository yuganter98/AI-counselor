from pydantic import BaseModel
from typing import List, Optional, Literal
from app.models.models import UserStageEnum

class AIInput(BaseModel):
    # Context usually comes from user in DB, but maybe frontend sends specific query?
    # For now, simplistic trigger.
    message: Optional[str] = None

class AIActionType(str):
    SHORTLIST = "SHORTLIST"
    LOCK = "LOCK"
    TRANSITION = "TRANSITION"

class AIAction(BaseModel):
    type: str # SHORTLIST, LOCK, TRANSITION
    label: str # "Shortlist Global Tech", "Move onto Discovery"
    payload: dict # e.g. {"university_id": 1} or {"target_stage": "DISCOVERY"}

class AIResponse(BaseModel):
    message: str
    actions: List[AIAction] = []
    next_suggestion: str

class ActionRequest(BaseModel):
    action_type: str
    payload: dict
