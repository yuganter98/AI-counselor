from fastapi import APIRouter, Depends
from app.api import deps
from app.models.models import User, UserStageEnum

router = APIRouter()

@router.get("/protected/discovery")
def discovery_content(
    user: User = Depends(deps.require_stage(UserStageEnum.DISCOVERY))
):
    return {"message": "Welcome to Discovery Phase", "user": user.email}

@router.get("/protected/profile")
def profile_content(
    user: User = Depends(deps.require_stage(UserStageEnum.PROFILE))
):
    return {"message": "Welcome to Profile Phase", "user": user.email}
