import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from app.models.ufc_models import MainEvent, EventSummary, Fight, Event
import pycountry

class UFCScraper:
    def __init__(self):
        self.base_url = "https://www.ufc.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def get_upcoming_event_links(self) -> List[str]:
        """
        Scrapes all upcoming UFC events by paginating the AJAX endpoint.
        Returns a list of event links.
        """
        event_links = []
        page = 0
        while True:
            ajax_url = (
                f"{self.base_url}/views/ajax"
                "?view_name=events_upcoming_past"
                "&view_display_id=upcoming"
                "&view_args="
                "&view_path=%2Fevents"
                "&view_base_path="
                "&view_dom_id=some_random_id"
                "&pager_element=0"
                f"&page={page}"
                "&ajax_page_state%5Btheme%5D=ufc"
                "&ajax_page_state%5Btheme_token%5D="
                "&ajax_page_state%5Blibraries%5D="
            )
            response = requests.get(ajax_url, headers=self.headers)
            if response.status_code != 200 or not response.text.strip():
                break

            try:
                data = response.json()
                html = None
                for part in data:
                    if isinstance(part, dict) and 'data' in part and '<article' in part['data']:
                        html = part['data']
                        break
                if not html:
                    break
                soup = BeautifulSoup(html, "html.parser")
                for container in soup.find_all("article", class_="c-card-event--result"):
                    href = container.find("a").get("href")
                    event_link = f"{self.base_url}{href}"
                    event_links.append(event_link)
            except Exception as e:
                print(f"Error parsing AJAX response: {e}")
                break

            page += 1

        return event_links
    
    def _extract_fighter_name(self, link_element: BeautifulSoup) -> str:
        """
        Extracts the fighter's name from the link element.
        Handles cases where the name is in <span> tags or as direct text in <a> tag.
        """
        given_name_span = link_element.find("span", class_="c-listing-fight__corner-given-name")
        family_name_span = link_element.find("span", class_="c-listing-fight__corner-family-name")
        if given_name_span and family_name_span:
            return f"{given_name_span.text.strip()} {family_name_span.text.strip()}"
        a_tag = link_element.find("a")
        if a_tag:
            return a_tag.get_text(strip=True)
        return ""
    
    def _get_flag_image_url(self, location: str) -> str:
        """
        Finds a flag image from the location string using flagcdn.com.
        Returns the flag image URL or an empty string if no flag is found.
        """
        country_name = location.split(",")[-1].strip()
        country = pycountry.countries.get(name=country_name)
        country_code = country.alpha_2 if country else ""

        if country_code:
            return f"https://flagcdn.com/w320/{country_code.lower()}.png"
        return ""

    def _normalize_image_url(self, image_url: str) -> str:
        """
        Ensures the image URL is absolute by prepending base_url if necessary.
        """
        if image_url and not image_url.startswith("http"):
            return f"{self.base_url}{image_url}"
        return image_url

    def get_main_event_data(self, event_link: str) -> MainEvent:
        """
        Scrapes the fight data for the main event of a UFC event.
        Returns a MainEvent model.
        """
        response = requests.get(event_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        fight_container = soup.find("li", class_="l-listing__item")
        if not fight_container:
            return None

        fighter_1_link_element = fight_container.find("div", class_="c-listing-fight__corner-name c-listing-fight__corner-name--red")
        fighter_1_link = fighter_1_link_element.find("a").get("href")
        fighter_1_name = self._extract_fighter_name(fighter_1_link_element)

        fighter_2_link_element = fight_container.find("div", class_="c-listing-fight__corner-name c-listing-fight__corner-name--blue")
        fighter_2_link = fighter_2_link_element.find("a").get("href")
        fighter_2_name = self._extract_fighter_name(fighter_2_link_element)

        fighter_images = fight_container.find_all("img", class_="image-style-event-fight-card-upper-body-of-standing-athlete")
        fighter_1_image = self._normalize_image_url(fighter_images[0].get("src"))
        fighter_2_image = self._normalize_image_url(fighter_images[1].get("src"))

        ranks_row = fight_container.find("div", class_="c-listing-fight__ranks-row")
        fighter_1_rank = ""
        fighter_2_rank = ""
        if ranks_row:
            rank_divs = ranks_row.find_all("div", class_="js-listing-fight__corner-rank")
            if len(rank_divs) >= 2:     
                fighter_1_rank = rank_divs[0].text.strip()
                fighter_2_rank = rank_divs[1].text.strip()

        main_event = MainEvent(
            event_url=event_link,
            fighter_1_link=fighter_1_link,
            fighter_2_link=fighter_2_link,
            fighter_1_name=fighter_1_name,
            fighter_2_name=fighter_2_name,
            fighter_1_image=fighter_1_image,
            fighter_2_image=fighter_2_image,
            fighter_1_rank=fighter_1_rank,
            fighter_2_rank=fighter_2_rank
        )

        return main_event
        
    def get_event_summary_data(self, event_link: str) -> EventSummary:
        """
        Scrapes the event data for the main event of a UFC event.
        Returns an EventSummary model.
        """
        response = requests.get(event_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        event_title = soup.find("div", class_="field field--name-node-title field--type-ds field--label-hidden field__item").text.strip()

        timestamp = None
        time_divs = soup.find_all("div", class_="c-event-fight-card-broadcaster__time tz-change-inner")
        if time_divs:
            timestamp = time_divs[-1].get("data-timestamp")
        if not timestamp:
            fallback_div = soup.find("div", class_="c-hero__headline-suffix tz-change-inner")
            timestamp = fallback_div.get("data-timestamp")
        if timestamp:
            event_date_utc = datetime.fromtimestamp(int(timestamp.strip()), tz=ZoneInfo("UTC"))
            event_date_bst = event_date_utc.astimezone(ZoneInfo("Europe/London"))
            if not time_divs:
                event_date_bst = event_date_bst.date()

        event_summary = EventSummary(
            event_url=event_link,
            event_title=event_title,
            event_date=event_date_bst,
        )
        return event_summary
    
    def get_fight_data(self, event_link: str) -> List[Fight]:
        """
        Scrapes the fight data of a UFC event.
        Returns a list of Fight models.
        """
        response = requests.get(event_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        fight_containers = soup.find_all("div", class_="c-listing-fight")
        if not fight_containers:
            return None
        
        fight_data_list = []
        
        for container in fight_containers:
            fighter_1_link_element = container.find("div", class_="c-listing-fight__corner-name c-listing-fight__corner-name--red")
            fighter_1_link = fighter_1_link_element.find("a").get("href")
            fighter_1_name = self._extract_fighter_name(fighter_1_link_element)
            
            fighter_2_link_element = container.find("div", class_="c-listing-fight__corner-name c-listing-fight__corner-name--blue")
            fighter_2_link = fighter_2_link_element.find("a").get("href")
            fighter_2_name = self._extract_fighter_name(fighter_2_link_element)
            
            fighter_images = container.find_all("img", class_="image-style-event-fight-card-upper-body-of-standing-athlete")
            fighter_1_image = self._normalize_image_url(fighter_images[0].get("src"))
            fighter_2_image = self._normalize_image_url(fighter_images[1].get("src"))
            
            ranks_row = container.find("div", class_="c-listing-fight__ranks-row")
            fighter_1_rank = ""
            fighter_2_rank = ""
            if ranks_row:
                rank_divs = ranks_row.find_all("div", class_="js-listing-fight__corner-rank")
                if len(rank_divs) >= 2:
                    fighter_1_rank = rank_divs[0].text.strip()
                    fighter_2_rank = rank_divs[1].text.strip()

            odds_row = container.find("div", class_="c-listing-fight__odds-row")

            red_country_div = odds_row.find("div", class_="c-listing-fight__country c-listing-fight__country--red")
            fighter_1_flag = red_country_div.find("img")["src"] if red_country_div.find("img") else ""

            blue_country_div = odds_row.find("div", class_="c-listing-fight__country c-listing-fight__country--blue")
            fighter_2_flag = blue_country_div.find("img")["src"] if blue_country_div.find("img") else ""

            fight_weight = container.find("div", class_="c-listing-fight__class-text").text.strip()

            fight_data = Fight(
                event_url=event_link,
                fighter_1_link=fighter_1_link,
                fighter_2_link=fighter_2_link,
                fighter_1_name=fighter_1_name,
                fighter_2_name=fighter_2_name,
                fighter_1_image=fighter_1_image,
                fighter_2_image=fighter_2_image,
                fighter_1_rank=fighter_1_rank,
                fighter_2_rank=fighter_2_rank,
                fighter_1_flag=fighter_1_flag,
                fighter_2_flag=fighter_2_flag,
                fight_weight=fight_weight
            )
            fight_data_list.append(fight_data)

        return fight_data_list
            

    def get_event_data(self, event_link: str) -> Event:
        """
        Scrapes the event data of a UFC event.
        Returns an Event model.
        """
        response = requests.get(event_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        event_title = soup.find("div", class_="field field--name-node-title field--type-ds field--label-hidden field__item").text.strip()

        timestamp = None
        time_divs = soup.find_all("div", class_="c-event-fight-card-broadcaster__time tz-change-inner")
        if time_divs:
            timestamp = time_divs[-1].get("data-timestamp")
        if not timestamp:
            fallback_div = soup.find("div", class_="c-hero__headline-suffix tz-change-inner")
            timestamp = fallback_div.get("data-timestamp")
        if timestamp:
            event_date_utc = datetime.fromtimestamp(int(timestamp.strip()), tz=ZoneInfo("UTC"))
            event_date_bst = event_date_utc.astimezone(ZoneInfo("Europe/London"))
            if not time_divs:
                event_date_bst = event_date_bst.date()

        location_div = soup.find("div", class_="field field--name-venue field--type-entity-reference field--label-hidden field__item")
        location_text = location_div.get_text(separator=" ", strip=True)
        parts = [part.strip() for part in location_text.replace('\n', ',').split(',') if part.strip()]
        event_venue = parts[0]
        event_location = ', '.join(parts[1:])

        event_location_flag = self._get_flag_image_url(event_location)

        event_data = Event(
            event_url=event_link,
            event_title=event_title,
            event_date=event_date_bst,
            event_venue=event_venue,
            event_location=event_location,
            event_location_flag=event_location_flag,
        )

        return event_data