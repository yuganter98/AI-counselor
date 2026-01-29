from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.models import User, Task, TaskStatus
from app.api import deps
from app.schemas.dashboard import DashboardSummary, ProfileStrength, StrengthComponent, TaskRead

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    user: User = Depends(deps.require_profile_complete),
):
    return DashboardSummary(
        name=user.name,
        email=user.email,
        current_stage=user.stage.current_stage,
        profile_completed=user.profile.profile_completed
    )

@router.get("/strength", response_model=ProfileStrength)
def get_profile_strength(
    user: User = Depends(deps.require_profile_complete),
    db: Session = Depends(get_db)
):
    # --- AUTO-SYNC: Repair Profile State based on Completed Tasks ---
    # This ensures that if a user completed a task but the side-effect failed,
    # simply loading the dashboard will fix it.
    
    completed_tasks = db.query(Task).filter(
        Task.user_id == user.id, 
        Task.status == TaskStatus.DONE
    ).all()
    
    p = user.profile
    dirty = False
    
    for t in completed_tasks:
        # SOP Sync
        if "Submit Application" in t.title or "Finalize SOP" in t.title:
            if p.sop_status != "Finalized":
                p.sop_status = "Finalized"
                dirty = True
        
        # Exams Sync
        if "Register for IELTS" in t.title:
            if p.ielts_status == "Not Taken":
                p.ielts_status = "Planned"
                dirty = True
        if "Register for GRE" in t.title:
            if p.gre_status == "Not Taken":
                p.gre_status = "Planned"
                dirty = True

    if dirty:
        db.commit()
        db.refresh(user)
        p = user.profile
    # -----------------------------------------------------------

    # 1. Academics Logic
    if p.gpa >= 3.5:
        acad_label = "Strong"
        acad_status = "success"
    elif p.gpa >= 3.0:
        acad_label = "Average"
        acad_status = "warning"
    else:
        acad_label = "Weak"
        acad_status = "error"
        
    # 2. Exams Logic
    # Simple logic: If IELTS/GRE taken -> Strong, Planned -> Average, Not Taken -> Weak
    exams_taken = 0
    if p.ielts_status == "Taken": exams_taken += 1
    if p.gre_status == "Taken": exams_taken += 1
    
    if exams_taken == 2:
        exam_label = "Strong"
        exam_status = "success"
        exam_val = "Both Taken"
    elif exams_taken == 1 or "Planned" in [p.ielts_status, p.gre_status] or "In Progress" in [p.ielts_status, p.gre_status] or "Prepared" in [p.ielts_status, p.gre_status]: 
        exam_label = "Average"
        exam_status = "warning"
        exam_val = "In Progress"
    else:
        exam_label = "Weak"
        exam_status = "error"
        exam_val = "Not Started"

    # 3. SOP Logic
    if p.sop_status in ["Done", "Finalized", "Reviewed"]:
        sop_label = "Strong"
        sop_status = "success"
    elif p.sop_status in ["Drafting", "Started"]:
        sop_label = "Average"
        sop_status = "warning"
    else:
        sop_label = "Weak"
        sop_status = "error"

    # Overall Logic
    if "Weak" in [acad_label, exam_label, sop_label]:
        overall_label = "WEAK"
        reason = "Critical gaps found in your profile."
    elif "Average" in [acad_label, exam_label, sop_label]:
        overall_label = "AVERAGE"
        reason = "Good foundation, but needs improvement."
    else:
        overall_label = "STRONG"
        reason = "You are ready for top universities!"

    # Determine Score Label
    score_display = f"{p.gpa}"
    if p.gpa > 20: 
        score_display = f"{p.gpa}%"
    else:
        score_display = f"{p.gpa} CGPA"

    return ProfileStrength(
        label=overall_label,
        reason=reason,
        components={
            "academics": StrengthComponent(label=acad_label, value=score_display, status=acad_status),
            "exams": StrengthComponent(label=exam_label, value=exam_val, status=exam_status),
            "sop": StrengthComponent(label=sop_label, value=p.sop_status or "Not Started", status=sop_status)
        }
    )

@router.get("/tasks", response_model=List[TaskRead])
def get_dashboard_tasks(
    user: User = Depends(deps.require_profile_complete),
    db: Session = Depends(get_db)
):
    # 1. Fetch existing
    existing_tasks = db.query(Task).filter(Task.user_id == user.id).all()
    existing_titles = {t.title for t in existing_tasks}
    
    new_tasks = []
    p = user.profile

    # 2. Generate Gaps (Additive Only)
    
    # Gap: Exams (If Weak/Average)
    if p.ielts_status in ["Not Taken", "Prepared"] and "Register for IELTS" not in existing_titles:
        new_tasks.append(Task(user_id=user.id, title="Register for IELTS", description="You need IELTS for most universities.", generated_by_ai=False))
    
    if p.gre_status in ["Not Taken", "Prepared"] and "Register for GRE" not in existing_titles:
         new_tasks.append(Task(user_id=user.id, title="Register for GRE", description="Check if your target course requires GRE.", generated_by_ai=False))
         
    # Gap: SOP
    if p.sop_status in ["Not Started", "Drafting"] and "Finalize SOP" not in existing_titles:
        if p.sop_status == "Not Started" and "Draft SOP" not in existing_titles:
             new_tasks.append(Task(user_id=user.id, title="Draft SOP", description="Start writing your Statement of Purpose.", generated_by_ai=False))
        elif p.sop_status == "Drafting":
             new_tasks.append(Task(user_id=user.id, title="Finalize SOP", description="Complete and review your SOP.", generated_by_ai=False))
        
    # Gap: Funding
    if (p.budget_max is None or p.budget_max < 20000) and "Explore Scholarships" not in existing_titles:
        new_tasks.append(Task(user_id=user.id, title="Explore Scholarships", description="Your budget is low or undefined. Look for funding options.", generated_by_ai=False))

    # 3. Persist
    if new_tasks:
        db.add_all(new_tasks)
        db.commit()
        # Refresh list
        return db.query(Task).filter(Task.user_id == user.id).all()
    
    return existing_tasks

@router.post("/tasks/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: int,
    user: User = Depends(deps.require_profile_complete),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = TaskStatus.DONE
    
    # --- Side Effects: Update Profile based on Task Completion ---
    p = user.profile
    
    # SOP Logic
    if "SOP" in task.title:
        if "Draft" in task.title:
             p.sop_status = "Drafting"
        elif "Finalize" in task.title:
             p.sop_status = "Finalized"
    
    # Implicit SOP Finalization via Application Submission
    if "Submit Application" in task.title:
        p.sop_status = "Finalized"
        
    # Exam Logic - Registration implies Planning/Preparation
    if "IELTS" in task.title and "Register" in task.title:
        # If they registered, they are at least "Planned" or "Prepared"
        if p.ielts_status == "Not Taken":
             p.ielts_status = "Planned"
             
    if "GRE" in task.title and "Register" in task.title:
         if p.gre_status == "Not Taken":
             p.gre_status = "Planned"

    # Assume taking test updates manually or via separate task? 
    # For now, let's auto-bump to "Planned" which is Average. 
    # User might need to manually set to "Taken" in settings or we generate a "Upload Score" task later.

    db.commit()
    db.refresh(task)
    return task
