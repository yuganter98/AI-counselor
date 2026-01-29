import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.models import User, UserStageEnum, Profile, Task, Shortlist
from app.services.action_executor import ActionExecutor

client = TestClient(app)

def setup_user_in_discovery(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.stage.current_stage = UserStageEnum.DISCOVERY
            user.profile.profile_completed = True
            
            # Clear shortlists
            db.query(Shortlist).filter(Shortlist.user_id==user.id).delete()
            db.commit()
    finally:
        db.close()
    return create_access_token(subject=email)

def test_finalize_flow():
    email = "profile@example.com"
    token = setup_user_in_discovery(email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Try Transition to FINALIZED without Shortlists (Should Fail)
    print("\n1. Try Transition with 0 shortlists (Should Fail)...")
    transition_action = {
        "action_type": "TRANSITION",
        "payload": {"target_stage": "FINALIZE"}
    }
    resp = client.post("/api/v1/ai/action/execute", json=transition_action, headers=headers)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    assert resp.status_code == 400

    # 2. Shortlist a Uni
    print("\n2. Shortlist a Uni...")
    # Seeded IDs exist? Let's assume ID 1 exists from seed step
    shortlist_action = {
        "action_type": "SHORTLIST",
        "payload": {"university_id": 1}
    }
    resp = client.post("/api/v1/ai/action/execute", json=shortlist_action, headers=headers)
    assert resp.status_code == 200

    # 3. Transition to FINALIZE (Should Success)
    print("\n3. Transition to FINALIZE...")
    resp = client.post("/api/v1/ai/action/execute", json=transition_action, headers=headers)
    assert resp.status_code == 200
    
    # 4. Check Finalize Status (Locked=0, Proceed=False)
    print("\n4. Check Status (Locked=0)...")
    resp = client.get("/api/v1/finalize/status", headers=headers)
    data = resp.json()
    print(f"Locked: {data['locked_count']}, Proceed: {data['can_proceed']}")
    assert data['locked_count'] == 0
    assert data['can_proceed'] == False
    
    # 5. Lock Uni (via AI Action logic or direct endpoint? Requirement: AI Suggests, User clicks. Frontend calls Endpoint or Execute?
    # Phase 5 requirements say: "POST /finalize/lock". 
    # AI logic suggests "LOCK" action type. 
    # ActionExecutor should handle LOCK action type too.
    # Let's test ActionExecutor LOCK.
    
    print("\n5. Execute LOCK Action...")
    lock_action = {
        "action_type": "LOCK",
        "payload": {"university_id": 1}
    }
    resp = client.post("/api/v1/ai/action/execute", json=lock_action, headers=headers)
    assert resp.status_code == 200
    
    # 6. Check Idempotency (Lock again)
    print("\n6. Lock again (Idempotent)...")
    resp = client.post("/api/v1/ai/action/execute", json=lock_action, headers=headers)
    print(f"Status: {resp.json()}")
    assert resp.json()['status'] == "ignored" or resp.json()['status'] == "success" # Executor returns success/ignored
    
    # 7. Check Status (Locked=1, Proceed=True)
    resp = client.get("/api/v1/finalize/status", headers=headers)
    data = resp.json()
    print(f"Locked: {data['locked_count']}, Proceed: {data['can_proceed']}")
    assert data['can_proceed'] == True
    
    # 8. Unlock
    print("\n8. Unlock...")
    resp = client.post("/api/v1/finalize/unlock", json={"university_id": 1}, headers=headers)
    assert resp.status_code == 200
    
    # 9. Verify Proceed=False
    resp = client.get("/api/v1/finalize/status", headers=headers)
    assert resp.json()['can_proceed'] == False
    
    print("\nFINALIZE FLOW VERIFIED!")

if __name__ == "__main__":
    test_finalize_flow()
