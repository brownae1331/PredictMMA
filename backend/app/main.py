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
    event_summary_data = ufc_scraper.get_event_summary_data(event_links[13])
    print(event_summary_data)
    return {"message": "API is running"}