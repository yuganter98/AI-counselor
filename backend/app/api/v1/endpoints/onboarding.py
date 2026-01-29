from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User, Profile
from app.schemas.schemas import OnboardingAcademic, OnboardingGoals, OnboardingBudget, OnboardingReadiness
from app.api import deps

router = APIRouter()

@router.post("/academic")
def onboarding_academic(
    data: OnboardingAcademic,
    user: User = Depends(deps.require_profile_incomplete),
    db: Session = Depends(get_db)
):
    profile = user.profile
    profile.education_level = data.education_level
    profile.major = data.major
    profile.graduation_year = data.graduation_year
    profile.gpa = data.gpa
    db.commit()
    return {"message": "Academic details saved"}

@router.post("/goals")
def onboarding_goals(
    data: OnboardingGoals,
    user: User = Depends(deps.require_profile_incomplete),
    db: Session = Depends(get_db)
):
    profile = user.profile
    profile.target_degree = data.target_degree
    profile.field_of_study = data.field_of_study
    profile.intake_year = data.intake_year
    profile.preferred_countries = data.preferred_countries
    db.commit()
    return {"message": "Goals saved"}

@router.post("/budget")
def onboarding_budget(
    data: OnboardingBudget,
    user: User = Depends(deps.require_profile_incomplete),
    db: Session = Depends(get_db)
):
    profile = user.profile
    profile.budget_min = data.budget_min
    profile.budget_max = data.budget_max
    profile.funding_type = data.funding_type
    db.commit()
    return {"message": "Budget saved"}

@router.post("/readiness")
def onboarding_readiness(
    data: OnboardingReadiness,
    user: User = Depends(deps.require_profile_incomplete),
    db: Session = Depends(get_db)
):
    profile = user.profile
    profile.ielts_status = data.ielts_status
    profile.gre_status = data.gre_status
    profile.sop_status = data.sop_status
    db.commit()
    return {"message": "Readiness saved"}

@router.post("/complete")
def complete_onboarding(
    user: User = Depends(deps.require_profile_incomplete),
    db: Session = Depends(get_db)
):
    # Validation: Ensure all fields are set (Basic check)
    p = user.profile
    if not all([p.major, p.target_degree, p.budget_max, p.ielts_status]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    p.profile_completed = True
    # NOTE: UserStage remains PROFILE as per Phase 2 requirements.
    db.commit()
    return {"message": "Onboarding completed", "profile_completed": True}
