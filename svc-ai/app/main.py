from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.ai import router as ai_router
from app.api.routes.vision import router as vision_router


app = FastAPI(
    title="Kora AI",
    description="Microservicio de Inteligencia Artificial de Kora",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
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