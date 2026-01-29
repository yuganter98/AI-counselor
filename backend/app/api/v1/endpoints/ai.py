from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User
from app.api import deps
from app.schemas.ai import AIInput, AIResponse, ActionRequest
from app.services.ai_service import AIService
from app.services.action_executor import ActionExecutor

router = APIRouter()

@router.post("/counsellor", response_model=AIResponse)
def talk_to_counsellor(
    input_data: AIInput,
    user: User = Depends(deps.get_current_user), # No strict profile guard, handling in logic
    db: Session = Depends(get_db)
):
    return AIService.reason(user, db)

@router.post("/action/execute")
def execute_action(
    request: ActionRequest,
    user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    return ActionExecutor.execute(request, user, db)
