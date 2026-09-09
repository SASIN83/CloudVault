import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine, SessionLocal
import app.models                                  # noqa: F401 — register models
from app.controllers import auth_controller, file_controller
from app.services import file_service

Base.metadata.create_all(bind=engine)              # dev convenience; Alembic in prod

PURGE_INTERVAL_SECONDS = 3600                      # hourly


async def _trash_purge_loop():
    while True:
        await asyncio.sleep(PURGE_INTERVAL_SECONDS)
        db = SessionLocal()
        try:
            n = file_service.purge_expired_trash(db)
            if n:
                print(f"[purge] removed {n} expired trash item(s) from S3 + DB")
        except Exception as e:                     # never kill the loop
            print("[purge] error:", e)
        finally:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()                            # purge once at startup
    try:
        file_service.purge_expired_trash(db)
    finally:
        db.close()
    task = asyncio.create_task(_trash_purge_loop())
    yield
    task.cancel()


app = FastAPI(title="CloudVault API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|\d{1,3}(\.\d{1,3}){3})(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router)
app.include_router(file_controller.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}