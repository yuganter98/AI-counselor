import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.models import User, UserStageEnum
from app.services.action_executor import ActionExecutor
from app.schemas.ai import ActionRequest
from app.db.session import SessionLocal

def test():
    db = SessionLocal()
    print("--- ENUM DEBUG ---")
    print(f"Enum str check: '{str(UserStageEnum.PROFILE)}'")
    print(f"Enum value check: '{UserStageEnum.PROFILE.value}'")
    
    current_s = UserStageEnum.PROFILE
    print(f"Logic Check: '{str(current_s)}' == 'PROFILE' is {str(current_s) == 'PROFILE'}")
    print("------------------")

    user = db.query(User).first()
    if user:
        print(f"Test User: {user.email}")
        print(f"Current Stage: {user.stage.current_stage}")
        
        # Ensure we test the transition logic
        if user.stage.current_stage != UserStageEnum.PROFILE:
            print("Switching user back to PROFILE for testing...")
            user.stage.current_stage = UserStageEnum.PROFILE
            db.commit()
            
        req = ActionRequest(action_type="TRANSITION", payload={"target_stage": "DISCOVERY"})
        print("Attempting ActionExecutor.execute...")
        try:
            res = ActionExecutor.execute(req, user, db)
            print("Execution Result:", res)
            print(f"User Stage After: {user.stage.current_stage}")
        except Exception as e:
            print("Execution Failed with Error:", e)
            import traceback
            traceback.print_exc()
            
    db.close()

if __name__ == "__main__":
    test()
