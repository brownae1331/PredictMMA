from fastapi import FastAPI, Depends
from app.core.config import add_cors
from app.api.auth_routes import router as auth_routes
from app.db.database import engine, get_db
from app.db.models import models
from app.api.predict_routes import router as predict_routes
from app.api.event_routes import router as event_routes
from app.services.scraper_service import scrape_ufc_data
from sqlalchemy.orm import Session
from app.services.sherdog_scraper import SherdogScraper

app = FastAPI()

add_cors(app)

models.Base.metadata.create_all(bind=engine)

# app.include_router(ufc_routes, prefix="/ufc", tags=["UFC"])
app.include_router(event_routes, prefix="/events", tags=["Events"])
app.include_router(auth_routes, prefix="/auth", tags=["Auth"])
app.include_router(predict_routes, prefix="/predict", tags=["Predict"])

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    """Root endpoint: trigger a full UFC data scrape and seeding operation."""
    scrape_ufc_data(db, scrape_previous=False, scrape_upcoming=True)
    # scraper = SherdogScraper()
    # fights = scraper.get_upcoming_event_fights("https://www.sherdog.com/events/UFC-on-ESPN-71-Albazi-vs-Taira-108019")
    # for fight in fights:
    #     print(f"Fight: {fight.fighter_1_url} vs {fight.fighter_2_url}")
    return {"message": "Database updated with latest UFC data."}