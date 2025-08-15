from fastapi import FastAPI, Depends
from app.core.config import add_cors
from app.db.database import engine, get_db
from app.db.models import models
from app.api.auth_routes import router as auth_routes
from app.api.predict_routes import router as predict_routes
from app.api.event_routes import router as event_routes
from app.api.fight_routes import router as fight_routes
from app.services.orchestrator.ufc_coordinator import UFCScraperCoordinator
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import time
import os

app = FastAPI()

add_cors(app)

# Wait for the database to be ready before creating tables
def init_db_with_retry() -> None:
    retries = int(os.getenv("DB_INIT_RETRIES", "20"))
    delay_seconds = int(os.getenv("DB_INIT_DELAY_SECONDS", "2"))
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)
            return
        except OperationalError as exc:
            last_error = exc
            print(f"Database not ready (attempt {attempt}/{retries}). Retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)
    # If we exhausted retries, re-raise the last error
    if last_error is not None:
        raise last_error

init_db_with_retry()

app.include_router(auth_routes, prefix="/auth", tags=["Auth"])
app.include_router(predict_routes, prefix="/predict", tags=["Predict"])
app.include_router(event_routes, prefix="/events", tags=["Events"])
app.include_router(fight_routes, prefix="/fights", tags=["Fights"])

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    """Root endpoint: trigger a full UFC data scrape and seeding operation (async via Celery)."""
    ufc_coordinator = UFCScraperCoordinator()
    print("Starting UFC sync...")
    task_id = ufc_coordinator.test_task()
    return {"message": "UFC sync scheduled.", "task_id": task_id}