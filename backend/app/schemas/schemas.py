from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.models.models import UserStageEnum

# Auth Schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    profile_completed: bool
    current_stage: UserStageEnum

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Onboarding Schemas
class OnboardingAcademic(BaseModel):
    education_level: str
    major: str
    graduation_year: int
    gpa: float

class OnboardingGoals(BaseModel):
    target_degree: str
    field_of_study: str
    intake_year: int
    preferred_countries: List[str]

class OnboardingBudget(BaseModel):
    budget_min: int
    budget_max: int
    funding_type: str

class OnboardingReadiness(BaseModel):
    ielts_status: str
    gre_status: str
    sop_status: str
