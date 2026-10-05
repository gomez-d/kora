from typing import Literal, Optional

from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    type: Literal["llm", "vision"]

    prompt: Optional[str] = Field(
        default=None,
        min_length=1
    )

    user_id: Optional[str] = None


class Detection(BaseModel):
    food: str
    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

class LLMResponse(BaseModel):
    success: bool
    type: Literal["llm"]
    response: str

class AIErrorResponse(BaseModel):
    success: bool = False
    type: str
    error: str

class VisionResponse(BaseModel):
    success: bool
    detections: list[Detection]