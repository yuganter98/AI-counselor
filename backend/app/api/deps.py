from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.models import User, UserStageEnum

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
        if token_data is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
    except (JWTError, ValidationError):
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    
    user = db.query(User).filter(User.email == token_data).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def require_stage(required_stage: UserStageEnum):
    """
    Stage Guard Utility:
    Blocks API access if user is not in the required stage.
    Enforces STRICT EXACT MATCH.
    """
    def stage_checker(user: User = Depends(get_current_user)):
        # Backend Authority: Frontend cannot infer or override stages.
        if not user.stage:
             raise HTTPException(status_code=400, detail="User has no stage assigned")
             
        if user.stage.current_stage != required_stage:
            raise HTTPException(
                status_code=403,
                detail=f"Access forbidden: User is in stage {user.stage.current_stage.value}, required {required_stage.value}"
            )
        return user
    return stage_checker

def require_profile_incomplete(user: User = Depends(get_current_user)):
    """
    Blocks access if profile is already complete.
    Used for Onboarding routes.
    """
    if user.profile and user.profile.profile_completed:
        raise HTTPException(
            status_code=400,
            detail="Profile already completed. Cannot access onboarding."
        )
    return user

def require_profile_complete(user: User = Depends(get_current_user)):
    """
    Blocks access if profile is incomplete.
    Used for Dashboard/Core routes.
    """
    if not user.profile or not user.profile.profile_completed:
        raise HTTPException(
            status_code=403,
            detail="Profile incomplete. Please complete onboarding first."
        )
    return user
