from fastapi import FastAPI, Depends
from app.core.config import add_cors
from app.api.ufc_routes import router as ufc_routes
from app.api.auth_routes import router as auth_routes
from app.db.database import engine, get_db
from app.db.models import models
from app.api.predict_routes import router as predict_routes
from app.services.sherdog_scraper import SherdogScraper
from app.services.event_service import upsert_events
from app.services.fight_service import upsert_fights
from sqlalchemy.orm import Session

app = FastAPI()

add_cors(app)

models.Base.metadata.create_all(bind=engine)

app.include_router(ufc_routes, prefix="/ufc", tags=["UFC"])
app.include_router(auth_routes, prefix="/auth", tags=["Auth"])
app.include_router(predict_routes, prefix="/predict", tags=["Predict"])

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    """Root endpoint: scrape previous UFC events and persist them."""
    sherdog_scraper = SherdogScraper()
    previous_events = sherdog_scraper.get_previous_events()
    upcoming_events = sherdog_scraper.get_upcoming_events()

    # Store events in DB (idempotent operation)
    upsert_events(previous_events, db)
    upsert_events(upcoming_events, db)

    # Scrape and persist fights for each previous event
    for event in previous_events:
        print(f"Scraping fights for event: {event.event_title}")
        fights = sherdog_scraper.get_previous_event_fights(event.event_url)
        upsert_fights(fights, db)

    return {
        "message": "API is running",
        "events": previous_events + upcoming_events,
    }