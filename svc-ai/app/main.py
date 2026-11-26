import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv


# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Import routers after loading environment variables
def load_routers():
    from app.api.routes.ai import router as ai_router
    from app.api.routes.vision import router as vision_router

    return ai_router, vision_router


ai_router, vision_router = load_routers()


app = FastAPI(
    title="Kora AI",
    description="Microservicio de Inteligencia Artificial de Kora",
    version="1.0.0"
)


# CORS
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ai_router)
app.include_router(vision_router)


@app.get("/")
def root():
    return {
        "service": "svc-ai",
        "status": "running"
    }
