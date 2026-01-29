from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User, Profile, UserStage, UserStageEnum
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.schemas import UserSignup, UserLogin, Token, UserResponse
from app.api import deps

router = APIRouter()

@router.post("/signup", response_model=Token)
def signup(user_in: UserSignup, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    # Create User
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create Empty Profile
    profile = Profile(user_id=new_user.id, profile_completed=False)
    db.add(profile)

    # Create Stage (Strictly PROFILE)
    stage = UserStage(user_id=new_user.id, current_stage=UserStageEnum.PROFILE)
    db.add(stage)

    db.commit()
    db.refresh(new_user) # Refresh to load relationships

    access_token = create_access_token(subject=new_user.email)
    
    # Construct response manually to ensure fields are populated
    user_resp = UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        profile_completed=new_user.profile.profile_completed,
        current_stage=new_user.stage.current_stage
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_resp
    }

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(subject=user.email)

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        profile_completed=user.profile.profile_completed,
        current_stage=user.stage.current_stage
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_resp
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(deps.get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile_completed=current_user.profile.profile_completed,
        current_stage=current_user.stage.current_stage
    )
