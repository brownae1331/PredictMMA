import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class UFCEventsScraper:
    def __init__(self):
        self.url = "https://www.tapology.com/fightcenter/promotions/1-ultimate-fighting-championship-ufc"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_event_links(self):
        """Scrapes the UFC events and returns the links to the events"""
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        event_links = []
        
        event_containers = soup.find_all("div", class_="div flex flex-col border-b border-solid border-neutral-700")
        
        for container in event_containers:
            href = container.find("a", class_="border-b border-tap_3 border-dotted hover:border-solid").get("href")
            event_link = f"https://www.tapology.com{href}"
            event_links.append(event_link)
        
        return event_links

    def get_upcoming_event_links(self):
        """Scrapes the event links and returns the links to the upcoming events"""
        event_links = self.get_event_links()
        upcoming_event_links = []
        for link in event_links:
            response = requests.get(link, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")

            data_container = soup.find("div", attrs={"class": "div hidden md:flex flex-col md:w-[338px]"})

            # date_span = soup.find("span", string="Date/Time:")
            # date_container = date_span.parent
            
            # date_span = date_container.find("span", class_="text-neutral-700")
            # event_date = date_span.text.strip()
            # print(event_date)
        return upcoming_event_links