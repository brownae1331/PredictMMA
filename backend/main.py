from fastapi import FastAPI
from ufc_scraper import UFCEventsScraper

app = FastAPI()

@app.get("/")
def read_root():
    scraper = UFCEventsScraper()
    return scraper.get_upcoming_event_links()
