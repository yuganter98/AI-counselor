import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.models import User, UserStageEnum, Shortlist, Task
from app.services.action_executor import ActionExecutor

client = TestClient(app)

def setup_user_in_finalize(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.stage.current_stage = UserStageEnum.FINALIZE
            user.profile.profile_completed = True
            
            # Clear old stuff
            db.query(Shortlist).filter(Shortlist.user_id==user.id).delete()
            db.query(Task).filter(Task.user_id==user.id).delete()
            
            # Create a locked shortlist (ID 1)
            sh = Shortlist(user_id=user.id, university_id=1, category="TARGET", locked=True)
            db.add(sh)
            db.commit()
    finally:
        db.close()
    return create_access_token(subject=email)

def test_application_flow():
    email = "profile@example.com"
    token = setup_user_in_finalize(email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Start Application Phase
    print("\n1. Start Application Phase...")
    resp = client.post("/api/v1/application/start", headers=headers)
    print(f"Msg: {resp.json().get('message')}")
    assert resp.status_code == 200
    
    # 2. Check Tasks Generated
    print("\n2. Check Generated Tasks...")
    resp = client.get("/api/v1/application/tasks", headers=headers)
    tasks = resp.json()
    print(f"Tasks Found: {len(tasks)}")
    
    # Needs at least 3 tasks for the 1 locked uni
    # Assuming Task Gen creates 3 per uni
    uni1_tasks = [t for t in tasks if t['university_id'] == 1]
    assert len(uni1_tasks) >= 3
    print("Tasks verified for Uni ID 1.")
    
    # 3. Test Idempotency (Call Start again)
    print("\n3. Call Start again (Idempotent)...")
    resp = client.post("/api/v1/application/start", headers=headers)
    assert resp.status_code == 200
    # Task count should match exactly, no dupes
    resp = client.get("/api/v1/application/tasks", headers=headers)
    new_tasks = resp.json()
    assert len(new_tasks) == len(tasks)
    
    # 4. Unlock and Check Cleanup
    # Problem: Unlock requires FINALIZE stage in router?
    # finalize.py: Deps.require_stage(FINALIZE)
    # If we moved to APPLICATION, can we unlock?
    # Requirement: "If a locked university is unlocked: Remove its application-specific tasks"
    # But does the system allow unlocking in APPLICATION stage?
    # Usually you'd go back or have specific permission.
    # Let's check `finalize.py`. It uses `deps.require_stage(UserStageEnum.FINALIZE)`.
    # Phase 6 Entry Conditions: current_stage = APPLICATION.
    # So if I am in APPLICATION, I cannot call /finalize/unlock if it strictly requires FINALIZE.
    # BUT, Application Phase implies we are executing.
    # Maybe we need to update finalize.py to allow APPLICATION stage too?
    # Or maybe Application phase has a "Back to Finalize" action?
    # Assuming for this Phase 6 scope, if user wants to unlock, they might strictly need to be in FINALIZE.
    # But let's assume valid flow: maybe user realizes "Wait, I don't want this uni".
    # User Request: "If a locked university is unlocked..." implies it's possible.
    # I will modify my test to manually set stage back to FINALIZE to test cleanup, OR update endpoint to allow APPLICATION.
    # Updating endpoint is better UX. I'll modify finalize.py permissions.
    pass

    print("\nTESTING CLEANUP (Simulated)...")
    # For test, let's force stage back to Finalize to check Unlock logic cleanly
    # (Or better, update endpoint).
    # I will update endpoint logic in next step if this fails, but for now let's verify logic by simulating stage.
    db = SessionLocal()
    u = db.query(User).filter(User.email==email).first()
    u.stage.current_stage = UserStageEnum.FINALIZE
    db.commit()
    db.close()
    
    resp = client.post("/api/v1/finalize/unlock", json={"university_id": 1}, headers=headers)
    assert resp.status_code == 200
    
    resp = client.get("/api/v1/application/tasks", headers=headers)
    tasks_after = resp.json()
    uni1_tasks_after = [t for t in tasks_after if t['university_id'] == 1]
    print(f"Tasks after unlock: {len(uni1_tasks_after)}")
    assert len(uni1_tasks_after) == 0
    
    print("\nAPPLICATION FLOW VERIFIED!")

if __name__ == "__main__":
    test_application_flow()
