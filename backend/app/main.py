from fastapi import FastAPI
from app.core.config import add_cors
from app.api.ufc_routes import router
from app.services.ufc_scraper import UFCScraper

app = FastAPI()

add_cors(app)

app.include_router(router, prefix="/ufc", tags=["UFC"])

@app.get("/")
def read_root():
    ufc_scraper = UFCScraper()
    event_links = ufc_scraper.get_upcoming_event_links()
    for event_link in event_links:
        event_data = ufc_scraper.get_event_data(event_link)
        print(event_data)
    return {"message": "API is running"}