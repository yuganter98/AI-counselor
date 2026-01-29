from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import User, UserStageEnum, Shortlist, ShortlistCategory
from app.schemas.ai import AIAction, ActionRequest


class ActionExecutor:
    @staticmethod
    def execute(request: ActionRequest, user: User, db: Session):
        # Fix: str(Enum) returns 'UserStageEnum.PROFILE', we want 'PROFILE'
        # Or simply cast to string and split, but .value is safer if it's a str Enum.
        current_stage = user.stage.current_stage.value if hasattr(user.stage.current_stage, 'value') else str(user.stage.current_stage)
        target_stage = request.payload.get("target_stage")
        
        print(f"DEBUG: EXECUTE ACTION. Current: {current_stage}, Target: {target_stage}")
        
        # 1. TRANSITION Action
        if request.action_type == "TRANSITION":
            
            # PROFILE -> DISCOVERY
            if current_stage == "PROFILE" and target_stage == "DISCOVERY":
                user.stage.current_stage = UserStageEnum.DISCOVERY
                db.commit()
                message = "Transitioned to Discovery Stage."
                print(f"DEBUG: SUCCESS - {message}")
                return {"status": "success", "message": message}

            # DISCOVERY -> FINALIZE
            elif current_stage == "DISCOVERY" and target_stage == "FINALIZE":
                 # Check if shortlists exist
                 count = db.query(Shortlist).filter(Shortlist.user_id == user.id).count()
                 if count == 0:
                     raise HTTPException(status_code=400, detail="Cannot finalize. No universities shortlisted.")
                
                 user.stage.current_stage = UserStageEnum.FINALIZE
                 db.commit()
                 return {"status": "success", "message": "Transitioned to Finalize Stage."}

            # FINALIZE -> APPLICATION
            elif current_stage == UserStageEnum.FINALIZE and target_stage == UserStageEnum.APPLICATION:
                 # Check Locks
                 locked_count = db.query(Shortlist).filter(
                     Shortlist.user_id == user.id, 
                     Shortlist.locked == True
                 ).count()
                 
                 if locked_count < 1:
                     raise HTTPException(status_code=400, detail="Cannot start application. No universities locked.")
                 
                 user.stage.current_stage = UserStageEnum.APPLICATION
                 
                 # Generate Tasks
                 from app.models.models import Task
                 locked_shortlists = db.query(Shortlist).filter(Shortlist.user_id == user.id, Shortlist.locked == True).all()
                 tasks_created = 0
                 for s in locked_shortlists:
                    uni_id = s.university_id
                    uni_name = s.university.name
                    existing = db.query(Task).filter(Task.user_id == user.id, Task.university_id == uni_id).count()
                    if existing == 0:
                        new_tasks = [
                            Task(user_id=user.id, university_id=uni_id, title=f"Draft SOP for {uni_name}", description="Customize your Statement of Purpose.", generated_by_ai=False),
                            Task(user_id=user.id, university_id=uni_id, title=f"Request Transcripts for {uni_name}", description="Contact your registrar.", generated_by_ai=False),
                            Task(user_id=user.id, university_id=uni_id, title=f"Submit Application Form for {uni_name}", description="Target submission before deadline.", generated_by_ai=False),
                        ]
                        db.add_all(new_tasks)
                        tasks_created += len(new_tasks)
                 
                 db.commit()
                 return {"status": "success", "message": f"Application Phase Started. {tasks_created} tasks generated."}
            
            else:
                raise HTTPException(status_code=403, detail="Invalid transition for current stage.")

        # 2. SHORTLIST Action
        elif request.action_type == "SHORTLIST":
            if current_stage != UserStageEnum.DISCOVERY:
                raise HTTPException(status_code=403, detail="Shortlisting only allowed in DISCOVERY stage.")
            
            uni_id = request.payload.get("university_id")
            if not uni_id:
                raise HTTPException(status_code=400, detail="Missing university_id.")
            
            # Idempotency
            exists = db.query(Shortlist).filter(Shortlist.user_id == user.id, Shortlist.university_id == uni_id).first()
            if exists:
                return {"status": "ignored", "message": "University already shortlisted."}
            
            # Default category TARGET for AI suggestions
            new_shortlist = Shortlist(
                user_id=user.id, 
                university_id=uni_id, 
                category=ShortlistCategory.TARGET
            )
            db.add(new_shortlist)
            db.commit()
            return {"status": "success", "message": "University shortlisted."}

        # 3. LOCK Action
        elif request.action_type == "LOCK":
            if current_stage != UserStageEnum.FINALIZE:
                 raise HTTPException(status_code=403, detail="Locking only allowed in FINALIZE stage.")
            
            uni_id = request.payload.get("university_id")
            # Logic similar to endpoint, reusing DB logic or calling internal
            shortlist = db.query(Shortlist).filter(
                Shortlist.user_id == user.id, 
                Shortlist.university_id == uni_id
            ).first()
            
            if not shortlist:
                raise HTTPException(status_code=404, detail="Shortlist not found.")
            
            if not shortlist.locked:
                shortlist.locked = True
                db.commit()
                return {"status": "success", "message": "University Locked."}
            
            return {"status": "ignored", "message": "Already locked."}

        else:
            raise HTTPException(status_code=400, detail="Unknown action type.")
