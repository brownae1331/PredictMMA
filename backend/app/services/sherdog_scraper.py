import requests
import cloudscraper
from bs4 import BeautifulSoup
from typing import List
from app.schemas.sherdog_schemas import Event
from urllib.parse import urljoin
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class SherdogScraper:
    def __init__(self):
        self.base_url = "https://www.sherdog.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def get_previous_events(self):
        """
        Scrapes every UFC event from Sherdog.
        Returns a list of events.
        """
        current_url = urljoin(self.base_url, "/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/1")
        events = []
        current_page = 1

        while current_url:
            print(f"Scraping page {current_page}...")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(current_url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")

            events_container = soup.find("div", id="recent_tab")
            for tr in events_container.find_all("tr", itemtype="http://schema.org/Event"):
                event_url = urljoin(self.base_url, tr.find("a", itemprop="url")["href"])
                event_title = tr.find("span", itemprop="name").text.strip()
                
                start_raw  = tr.find("meta", itemprop="startDate")["content"]
                dt = datetime.fromisoformat(start_raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                event_date = dt.astimezone(ZoneInfo("Europe/London"))

                location = tr.find("td", itemprop="location").get_text(" ", strip=True)
                
                events.append(Event(
                    event_url=event_url,
                    event_title=event_title,
                    event_date=event_date,
                    event_location=location,
                    event_organizer="UFC",
                ))

            pagination = events_container.find("span", class_="pagination")
            older_link = None
            if pagination:
                for a in pagination.find_all("a"):
                    if "Older Events" in a.text:
                        older_link = urljoin(self.base_url, a["href"])
                        break

            if older_link:
                current_url = older_link
            else:
                current_url = None

            current_page += 1

        return events