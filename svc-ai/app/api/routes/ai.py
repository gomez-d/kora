from fastapi import APIRouter, HTTPException

from app.schemas.ai import (
    AIRequest,
    LLMResponse
)

from app.services.ai_service import AIService


router = APIRouter()

ai_service = AIService()


@router.post("/ai/process", response_model=LLMResponse)
def process_ai(request: AIRequest):

    if request.type != "llm":
        raise HTTPException(
            status_code=400,
            detail="This endpoint only supports LLM requests"
        )

    if not request.prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt is required"
        )

    return ai_service.process_llm(
        request.prompt
    )