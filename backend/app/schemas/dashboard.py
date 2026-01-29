from pydantic import BaseModel
from typing import List, Optional
from app.models.models import UserStageEnum, TaskStatus

# Strength Schemas
class StrengthComponent(BaseModel):
    label: str  # Strong, Average, Weak
    value: str  # e.g., "3.8 GPA" or "IELTS Taken"
    status: str # success, warning, error (for UI color)

class ProfileStrength(BaseModel):
    label: str # STRONG, AVERAGE, WEAK
    reason: str
    components: dict[str, StrengthComponent] # academics, exams, sop

# Task Schemas
class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    generated_by_ai: bool

    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    name: str
    email: str
    current_stage: UserStageEnum
    profile_completed: bool
    # We could add more high-level info here
