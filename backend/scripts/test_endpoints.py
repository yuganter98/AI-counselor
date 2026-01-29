import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.models.models import User, UserStageEnum
from app.db.session import SessionLocal
from app.core.security import create_access_token

client = TestClient(app)

def get_token(email):
    return create_access_token(subject=email)

def test_access():
    # 1. Profile User trying to access Profile Route (Allowed)
    token_profile = get_token("profile@example.com")
    headers_profile = {"Authorization": f"Bearer {token_profile}"}
    
    print("Testing PROFILE user accessing PROFILE route...")
    resp = client.get("/api/v1/test/protected/profile", headers=headers_profile)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    assert resp.status_code == 200

    # 2. Profile User trying to access Discovery Route (Forbidden)
    print("\nTesting PROFILE user accessing DISCOVERY route...")
    resp = client.get("/api/v1/test/protected/discovery", headers=headers_profile)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    assert resp.status_code == 403

    # 3. Discovery User trying to access Discovery Route (Allowed)
    token_discovery = get_token("discovery@example.com")
    headers_discovery = {"Authorization": f"Bearer {token_discovery}"}
    
    print("\nTesting DISCOVERY user accessing DISCOVERY route...")
    resp = client.get("/api/v1/test/protected/discovery", headers=headers_discovery)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    assert resp.status_code == 200
    
    # 4. Discovery User trying to access Profile Route (Forbidden - Exact Match)
    print("\nTesting DISCOVERY user accessing PROFILE route...")
    resp = client.get("/api/v1/test/protected/profile", headers=headers_discovery)
    print(f"Status: {resp.status_code}, Msg: {resp.json()}")
    assert resp.status_code == 403

    print("\nALL TESTS PASSED!")

if __name__ == "__main__":
    test_access()
