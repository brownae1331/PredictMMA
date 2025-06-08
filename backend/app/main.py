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
    print(event_links)
    main_event_data = ufc_scraper.get_main_event_data(event_links[4])
    print(main_event_data)
    return {"message": "API is running"}
