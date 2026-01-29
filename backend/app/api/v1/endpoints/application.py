from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.models import User, Shortlist, UserStageEnum, Task, TaskStatus
from app.api import deps
from pydantic import BaseModel

router = APIRouter()

class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    university_id: Optional[int] = None
    university_name: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/start")
def start_application_phase(
    user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate State
    if user.stage.current_stage == UserStageEnum.APPLICATION:
        # Idempotent: Just return success, tasks check comes next
        pass
    elif user.stage.current_stage == UserStageEnum.FINALIZE:
         # Check Locks
         locked_count = db.query(Shortlist).filter(
             Shortlist.user_id == user.id, 
             Shortlist.locked == True
         ).count()
         
         if locked_count < 1:
             raise HTTPException(status_code=400, detail="Cannot start application. No universities locked.")
         
         user.stage.current_stage = UserStageEnum.APPLICATION
         db.commit()
    else:
        raise HTTPException(status_code=403, detail="Invalid stage for Application Start.")
    
    # 2. Generate Tasks Logic
    locked_shortlists = db.query(Shortlist).filter(
        Shortlist.user_id == user.id, 
        Shortlist.locked == True
    ).all()
    
    tasks_created = 0
    for s in locked_shortlists:
        uni_id = s.university_id
        uni_name = s.university.name
        
        # Check if tasks exist for this uni
        existing = db.query(Task).filter(
            Task.user_id == user.id,
            Task.university_id == uni_id
        ).count()
        
        if existing == 0:
            # Generate Standard Checklist
            new_tasks = [
                Task(user_id=user.id, university_id=uni_id, title=f"Draft SOP for {uni_name}", description="Customize your Statement of Purpose.", generated_by_ai=False),
                Task(user_id=user.id, university_id=uni_id, title=f"Request Transcripts for {uni_name}", description="Contact your registrar.", generated_by_ai=False),
                Task(user_id=user.id, university_id=uni_id, title=f"Submit Application Form for {uni_name}", description="Target submission before deadline.", generated_by_ai=False),
            ]
            db.add_all(new_tasks)
            tasks_created += len(new_tasks)
    
    if tasks_created > 0:
        db.commit()
    
    return {"status": "success", "message": f"Application Started. Generated tasks for {len(locked_shortlists)} universities."}

@router.get("/tasks", response_model=List[TaskRead])
def get_application_tasks(
    user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch tasks, explicitly join for safety if needed, but manual population OK for basic
    tasks = db.query(Task).filter(Task.user_id == user.id).all()
    
    # Enhance specific tasks with uni details if available
    # Actually Task model has 'university' relationship, so Pydantic should handle if we map it
    # But let's build response explicitly to be safe or ensure eager loading?
    # Relationship is lazy by default. 
    
    return [
        TaskRead(
            id=t.id,
            title=t.title,
            description=t.description,
            status=t.status,
            university_id=t.university_id,
            university_name=t.university.name if t.university else (None)
        )
        for t in tasks
    ]

@router.post("/tasks/{task_id}/complete")
def complete_app_task(
    task_id: int,
    user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = TaskStatus.DONE
    db.commit()
    return {"status": "success", "task_id": task_id}
