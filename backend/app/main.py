from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
import app.models                                  # noqa: F401 — register models
from app.controllers import auth_controller, file_controller

Base.metadata.create_all(bind=engine)              # dev convenience; use Alembic in prod

app = FastAPI(title="CloudVault API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router)
app.include_router(file_controller.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}