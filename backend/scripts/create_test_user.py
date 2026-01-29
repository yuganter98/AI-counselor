import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.models import User, UserStage, UserStageEnum, Profile
from app.core.security import get_password_hash, create_access_token

def create_user(email, stage_enum):
    db = SessionLocal()
    try:
        # Check if exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                name="Test User",
                email=email,
                password_hash=get_password_hash("password123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Add Stage
            stage = UserStage(user_id=user.id, current_stage=stage_enum)
            db.add(stage)
            
            # Add Profile (Empty)
            profile = Profile(user_id=user.id, profile_completed=False)
            db.add(profile)
            
            db.commit()
            print(f"User {email} created.")
        else:
            print(f"User {email} already exists.")
            # Update stage if needed
            if user.stage:
                user.stage.current_stage = stage_enum
                db.commit()
        
        token = create_access_token(subject=email)
        print(f"Stage: {stage_enum.value}")
        print(f"Token: {token}")
        return token
    except Exception as e:
        print(f"Error creating user repr: {repr(e)}")
        from app.core.config import settings
        print(f"DB URI: {settings.SQLALCHEMY_DATABASE_URI}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating PROFILE user...")
    create_user("profile@example.com", UserStageEnum.PROFILE)
    print("\nCreating DISCOVERY user...")
    create_user("discovery@example.com", UserStageEnum.DISCOVERY)
