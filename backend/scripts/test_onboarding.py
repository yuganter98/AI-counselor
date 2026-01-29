import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.api.v1.endpoints import onboarding
# We use requests + running server or TestClient? 
# TestClient is better.
from fastapi.testclient import TestClient
# We use requests + running server or TestClient? 
# TestClient is better.
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup_onboarding_flow():
    # 1. Signup
    print("1. Signing up new user...")
    signup_data = {
        "name": "New Student",
        "email": "student@example.com",
        "password": "strongpassword"
    }
    resp = client.post("/api/v1/auth/signup", json=signup_data)
    if resp.status_code == 400 and "already exists" in resp.text:
        # Login if exists
        print("User exists, logging in...")
        login_resp = client.post("/api/v1/auth/login", json={"email": "student@example.com", "password": "strongpassword"})
        token = login_resp.json()["access_token"]
        user_info = login_resp.json()["user"]
    else:
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        user_info = resp.json()["user"]
    
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Logged in. Profile Completed: {user_info['profile_completed']}, Stage: {user_info['current_stage']}")
    
    # 2. Try to Complete immediately (Should fail validation)
    print("\n2. Trying early completion (Should fail)...")
    resp = client.post("/api/v1/onboarding/complete", headers=headers)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    if user_info['profile_completed'] == False:
        assert resp.status_code == 400 # specific validation error
    
    # 3. Fill details
    print("\n3. Filling Academic...")
    client.post("/api/v1/onboarding/academic", json={
        "education_level": "Undergrad",
        "major": "CS",
        "graduation_year": 2025,
        "gpa": 3.8
    }, headers=headers)

    print("Filling Goals...")
    client.post("/api/v1/onboarding/goals", json={
        "target_degree": "Masters",
        "field_of_study": "AI",
        "intake_year": 2026,
        "preferred_countries": ["USA", "Germany"]
    }, headers=headers)

    print("Filling Budget...")
    client.post("/api/v1/onboarding/budget", json={
        "budget_min": 10000,
        "budget_max": 50000,
        "funding_type": "Self + Loan"
    }, headers=headers)

    print("Filling Readiness...")
    client.post("/api/v1/onboarding/readiness", json={
        "ielts_status": "Not Taken",
        "gre_status": "Planned",
        "sop_status": "Not Started"
    }, headers=headers)

    # 4. Complete
    print("\n4. Completing Onboarding...")
    resp = client.post("/api/v1/onboarding/complete", headers=headers)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    assert resp.status_code == 200
    assert resp.json()["profile_completed"] == True

    # 5. Verify User State
    print("\n5. Verifying /me endpoint...")
    resp = client.get("/api/v1/auth/me", headers=headers)
    print(f"User State: {resp.json()}")
    assert resp.json()["profile_completed"] == True
    assert resp.json()["current_stage"] == "PROFILE"

    # 6. Try accessing Onboarding again (Should be blocked)
    print("\n6. Trying to access onboarding again (Should be Blocked)...")
    resp = client.post("/api/v1/onboarding/academic", json={}, headers=headers)
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 400 # or 403 based on implementation

    print("\nONBOARDING FLOW VERIFIED!")

if __name__ == "__main__":
    test_signup_onboarding_flow()
