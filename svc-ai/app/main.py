from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.ai import router as ai_router
from app.api.vision import router as vision_router

app = FastAPI(
    title="Kora AI",
    description="Microservicio de Inteligencia Artificial de Kora",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(ai_router)
app.include_router(vision_router)

@app.get("/")
def root():
    return {
        "service": "svc-ai",
        "status": "running"
    }