from fastapi import FastAPI, Depends
from app.core.config import add_cors
from app.db.database import engine, get_db
from app.db.models import models
from app.api.auth_routes import router as auth_routes
from app.api.predict_routes import router as predict_routes
from app.api.event_routes import router as event_routes
from app.api.fight_routes import router as fight_routes
from app.services.scraper_service import scrape_ufc_data
from app.services.fighter_update_service import update_all_fighters
from sqlalchemy.orm import Session

app = FastAPI()

add_cors(app)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth_routes, prefix="/auth", tags=["Auth"])
app.include_router(predict_routes, prefix="/predict", tags=["Predict"])
app.include_router(event_routes, prefix="/events", tags=["Events"])
app.include_router(fight_routes, prefix="/fights", tags=["Fights"])

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    """Root endpoint: trigger a full UFC data scrape and seeding operation."""
    scrape_ufc_data(db, scrape_previous=True, scrape_upcoming=True)
    # update_all_fighters(db)
    return {"message": "Database updated with latest UFC data."}