import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.models import User, Profile, Task

client = TestClient(app)

def create_user_with_profile(email, gpa, ielts, sop):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create fresh for test
             # Note: Using main app helper or just manual DB for speed
             # Manual is safer for test state
             pass
        else:
             # Update profile for test case
             user.profile.gpa = gpa
             user.profile.ielts_status = ielts
             user.profile.sop_status = sop
             user.profile.profile_completed = True
             
             # CLEAR tasks to test generation
             db.query(Task).filter(Task.user_id == user.id).delete()
             
             db.commit()
    finally:
        db.close()
    
    return create_access_token(subject=email)

def test_dashboard_logic():
    # 1. Test WEAK Profile
    email_weak = "profile@example.com" # reusing existing user
    token = create_user_with_profile(email_weak, gpa=2.5, ielts="Not Taken", sop="Not Started")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n1. Testing WEAK Profile...")
    resp = client.get("/api/v1/dashboard/strength", headers=headers)
    data = resp.json()
    print(f"Bkd Label: {data['label']}")
    assert data['label'] == "WEAK"
    
    print("Testing Task Generation for WEAK...")
    resp = client.get("/api/v1/dashboard/tasks", headers=headers)
    tasks = resp.json()
    titles = [t['title'] for t in tasks]
    print(f"Generated Tasks: {titles}")
    assert "Register for IELTS" in titles
    assert "Draft SOP" in titles
    
    # 2. Test STRONG Profile
    token = create_user_with_profile(email_weak, gpa=3.8, ielts="Taken", sop="Done")
    # Need to set GRE too for full strong
    db = SessionLocal()
    u = db.query(User).filter(User.email==email_weak).first()
    u.profile.gre_status = "Taken" 
    # NOTE: Tasks are persistent! So "Register for IELTS" should still be there but maybe we can mark done?
    # Requirement: "NEVER re-create a task that exists".
    # So if I update profile, old tasks remain. This is correct behavior.
    db.commit()
    db.close()
    
    print("\n2. Testing STRONG Profile (after update)...")
    resp = client.get("/api/v1/dashboard/strength", headers=headers)
    data = resp.json()
    print(f"Bkd Label: {data['label']}")
    assert data['label'] == "STRONG"
    
    # 3. Test Task Completion
    print("\n3. Testing Task Completion...")
    # Get ID of a task
    resp = client.get("/api/v1/dashboard/tasks", headers=headers)
    task_id = resp.json()[0]['id']
    
    resp = client.post(f"/api/v1/dashboard/tasks/{task_id}/complete", headers=headers)
    assert resp.status_code == 200
    assert resp.json()['status'] == "DONE"
    print("Task marked DONE.")

    print("\nDASHBOARD LOGIC VERIFIED!")

if __name__ == "__main__":
    test_dashboard_logic()
