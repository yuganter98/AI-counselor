from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User, Shortlist, UserStageEnum
from app.api import deps
from app.schemas.finalize import FinalizeStatus, ShortlistResponse, LockRequest

router = APIRouter()

def require_finalize_stage(user: User = Depends(deps.get_current_user)):
    if user.stage.current_stage not in [UserStageEnum.FINALIZE, UserStageEnum.APPLICATION]:
        # We allow application stage to view status, but modification might be restricted?
        # For Phase 5, strict check: modification only in FINALIZE.
        pass 
    return user

@router.get("/status", response_model=FinalizeStatus)
def get_finalize_status(
    user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    shortlists = db.query(Shortlist).filter(Shortlist.user_id == user.id).all()
    
    resp_list = []
    locked_count = 0
    for s in shortlists:
        if s.locked:
            locked_count += 1
        resp_list.append(ShortlistResponse(
            university_id=s.university.id,
            university_name=s.university.name,
            country=s.university.country,
            category=s.category,
            locked=s.locked
        ))
        
    return FinalizeStatus(
        shortlists=resp_list,
        locked_count=locked_count,
        can_proceed=locked_count >= 1
    )

@router.post("/lock")
def lock_university(
    req: LockRequest,
    user: User = Depends(deps.require_stage(UserStageEnum.FINALIZE)),
    db: Session = Depends(get_db)
):
    # Idempotent Lock
    shortlist = db.query(Shortlist).filter(
        Shortlist.user_id == user.id, 
        Shortlist.university_id == req.university_id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="University not found in shortlist.")
        
    if not shortlist.locked:
        shortlist.locked = True
        db.commit()
        
    return {"status": "success", "message": "University locked."}

@router.post("/unlock")
def unlock_university(
    req: LockRequest,
    user: User = Depends(deps.require_stage(UserStageEnum.FINALIZE)),
    db: Session = Depends(get_db)
):
    # Idempotent Unlock
    shortlist = db.query(Shortlist).filter(
        Shortlist.user_id == user.id, 
        Shortlist.university_id == req.university_id
    ).first()
    
    if not shortlist:
        raise HTTPException(status_code=404, detail="University not found in shortlist.")
        
    if shortlist.locked:
        shortlist.locked = False
        
        # CLEANUP: Remove pending tasks for this uni
        # We only remove pending? Or all? 
        # Requirement: "Remove its application-specific tasks"
        # Safe to remove all since they are tied to this specific application cycle logic.
        from app.models.models import Task
        db.query(Task).filter(
            Task.user_id == user.id,
            Task.university_id == req.university_id
        ).delete()
        
        db.commit()
        
    return {"status": "success", "message": "University unlocked."}
