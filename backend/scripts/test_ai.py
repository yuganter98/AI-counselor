import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.models import User, UserStageEnum, Profile, Task
from app.services.action_executor import ActionExecutor

client = TestClient(app)

def reset_user_stage(email, stage_enum, completed=True):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.stage.current_stage = stage_enum
            user.profile.profile_completed = completed
            # Ensure GPA/etc is set for Profile checks
            user.profile.gpa = 3.8
            db.commit()
    finally:
        db.close()
    return create_access_token(subject=email)

def test_ai_flow():
    email = "profile@example.com"
    token = reset_user_stage(email, UserStageEnum.PROFILE)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. PROFILE Stage -> Ask Counsellor
    print("\n1. Ask Counsel in PROFILE stage (Should suggest Transition)...")
    resp = client.post("/api/v1/ai/counsellor", json={"message": "What next?"}, headers=headers)
    print(f"Msg: {resp.json().get('message')}")
    actions = resp.json()['actions']
    print(f"Actions: {actions}")
    
    assert len(actions) > 0
    assert actions[0]['type'] == "TRANSITION"
    assert actions[0]['payload']['target_stage'] == "DISCOVERY"

    # 2. Try illegal SHORTLIST in PROFILE stage
    print("\n2. Try illegal SHORTLIST action in PROFILE stage (Should Fail)...")
    illegal_action = {
        "action_type": "SHORTLIST",
        "payload": {"university_id": 1}
    }
    resp = client.post("/api/v1/ai/action/execute", json=illegal_action, headers=headers)
    print(f"Status: {resp.status_code}, Det: {resp.json()}")
    assert resp.status_code == 403

    # 3. Execute Transition
    print("\n3. Execute TRANSITION action...")
    action = actions[0]
    execute_req = {
        "action_type": action['type'],
        "payload": action['payload']
    }
    resp = client.post("/api/v1/ai/action/execute", json=execute_req, headers=headers)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    assert resp.status_code == 200

    # 4. DISCOVERY Stage -> Ask Counsel
    # User should now be in Discovery
    print("\n4. Ask Counsel in DISCOVERY stage (Should suggest Unis)...")
    resp = client.post("/api/v1/ai/counsellor", json={"message": "Recommend unis"}, headers=headers)
    actions = resp.json()['actions']
    print(f"Actions found: {len(actions)}")
    if actions:
        print(f"First Action: {actions[0]}")
        assert actions[0]['type'] == "SHORTLIST"
        
        # 5. Execute Shortlist
        print("\n5. Execute SHORTLIST action...")
        shortlist_req = {
            "action_type": actions[0]['type'],
            "payload": actions[0]['payload']
        }
        resp = client.post("/api/v1/ai/action/execute", json=shortlist_req, headers=headers)
        assert resp.status_code == 200
        print("Shortlist success.")
        
        # 6. Idempotency Check
        print("\n6. Try duplicate SHORTLIST (Should be ignored)...")
        resp = client.post("/api/v1/ai/action/execute", json=shortlist_req, headers=headers)
        print(f"Msg: {resp.json()}")
        assert resp.json()['status'] == "ignored"

    print("\nAI FLOW VERIFIED!")

if __name__ == "__main__":
    test_ai_flow()
