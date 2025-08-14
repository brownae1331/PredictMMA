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
from app.tasks.tasks import debug_ping

app = FastAPI()

add_cors(app)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth_routes, prefix="/auth", tags=["Auth"])
app.include_router(predict_routes, prefix="/predict", tags=["Predict"])
app.include_router(event_routes, prefix="/events", tags=["Events"])
app.include_router(fight_routes, prefix="/fights", tags=["Fights"])

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    """Root endpoint: trigger a full UFC data scrape and seeding operation (async via Celery)."""
    ufc_coordinator = UFCScraperCoordinator()
    task_id = ufc_coordinator.schedule_sync_ufc_data()
    return {"message": "UFC sync scheduled.", "task_id": task_id}

@app.get("/celery/ping")
def celery_ping():
    """Dispatch a quick debug task to verify the worker is alive."""
    result = debug_ping.si("hello").delay()
    return {"task_id": result.id}

@app.get("/celery/result/{task_id}")
def celery_result(task_id: str):
    """Fetch the result/state of a task id."""
    async_result = debug_ping.AsyncResult(task_id)
    return {"state": async_result.state, "result": async_result.result}