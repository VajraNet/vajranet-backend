from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["Disaster AI Assistant"])


@router.post("/chat", summary="Query Disaster AI Assistant for Safety Instructions", status_code=status.HTTP_200_OK)
def emergency_ai_chat(
    request: AIChatRequest,
    db: Session = Depends(get_db)
):
    """
    Emergency disaster query assistant.
    Provides safety advice, flood/fire/earthquake protocols, and nearest verified shelter information.
    
    SAFETY NOTICE:
    - Never makes medical diagnoses or emergency medical decisions.
    - Never fabricates emergency resource availability.
    - Official disaster authorities retain all decision-making authority.
    """
    response_data = AIService.handle_emergency_chat(request, db)
    return success_response(
        data=response_data,
        message="AI safety response generated successfully"
    )
