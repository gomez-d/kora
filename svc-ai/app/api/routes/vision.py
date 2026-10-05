from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.ai_service import AIService


router = APIRouter()

ai_service = AIService()


@router.post("/vision/analyze")
async def analyze_vision(
    image: UploadFile = File(...)
):

    if not image.content_type:
        raise HTTPException(
            status_code=400,
            detail="Image type is required"
        )

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file must be an image"
        )

    contents = await image.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The image is empty"
        )

    return ai_service.process_vision(contents)