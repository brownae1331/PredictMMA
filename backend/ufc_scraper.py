import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

class UFCEventsScraper:
    def __init__(self):
        self.url = "https://www.tapology.com/fightcenter/promotions/1-ultimate-fighting-championship-ufc"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_event_links(self) -> list[str]:
        """Scrapes the UFC events and returns the links to the events"""
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        event_links = []
        
        event_containers = soup.find_all("div", class_="div flex flex-col border-b border-solid border-neutral-700")
        
        for container in event_containers:
            href = container.find("a", class_="border-b border-tap_3 border-dotted hover:border-solid").get("href")
            event_link = f"https://www.tapology.com{href}"
            event_links.append(event_link)
        
        return event_links[::-1]

    def get_upcoming_event_links(self) -> list[str]:
        """Scrapes the event links and returns the links to the upcoming events"""
        event_links = self.get_event_links()
        current_date = datetime.now().date()
        
        def check_event_date(session, link):
            try:
                response = session.get(link, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                date_span = soup.find("span", string="Date/Time:")
                if not date_span:
                    return None
                
                date_container = date_span.parent
                date_span = date_container.find("span", class_="text-neutral-700")
                
                if not date_span:
                    return None
                
                date_text = date_span.text.strip()
                event_date = (datetime.strptime(date_text, '%A %m.%d.%Y at %I:%M %p ET') + timedelta(days=1)).date()

                if event_date >= current_date:
                    print(event_date)
                    return link
            except Exception as e:
                print(f"Error processing {link}: {e}")
            return None
        
        # Use ThreadPoolExecutor for concurrent requests with session reuse
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all futures and map them to their original links
                future_to_link = {executor.submit(check_event_date, session, link): link for link in event_links}
                
                # Wait for all futures to complete and store results
                results = {}
                for future in as_completed(future_to_link):
                    link = future_to_link[future]
                    result = future.result()
                    results[link] = result
        
        # Build the upcoming_event_links list in the original order
        upcoming_event_links = []
        for link in event_links:
            if results.get(link):
                upcoming_event_links.append(results[link])
        
        return upcoming_event_links
    
    def get_event_data(self, event_link: str) -> dict:
        """Scrapes the event data and returns the data"""
        response = requests.get(event_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        date_span = soup.find("span", string="Date/Time:")
        date_container = date_span.parent
        
        date_span = date_container.find("span", class_="text-neutral-700")
        date_text = date_span.text.strip()

        event_date_et = datetime.strptime(date_text, '%A %m.%d.%Y at %I:%M %p ET').replace(tzinfo=ZoneInfo('America/New_York'))
        event_date_bst = event_date_et.astimezone(ZoneInfo('Europe/London'))

        event_data = {
            "event_title": soup.find("h2").text.strip(),
            "event_date": event_date_bst,
            "event_venue": soup.find("span", string="Venue:").parent.find("span", class_="text-neutral-700").text.strip(),
            "event_location": soup.find("span", string="Location:").parent.find("span", class_="text-neutral-700").text.strip(),
        }

        return event_data
    
    def get_fight_data(self, event_link: str) -> list[dict]:
        """Scrapes the fight data and returns data for each fight and fighter"""
        response = requests.get(event_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        fight_data_list = []
        fight_containers = soup.find_all("div", class_="div flex flex-col mt-3 mb-4 md:mt-2.5 md:mb-2.5 w-full fullsize")

        for container in fight_containers:
            fighter_links = list(set([f"https://www.tapology.com{link['href']}" for link in container.find_all("a", class_="link-primary-red")]))
            fighter_images = [img['src'] for img in container.find_all("img", class_="w-[77px] h-[77px] md:w-[104px] md:h-[104px] rounded")]

            fight_data = {
                "fighter_1": fighter_links[1],
                "fighter_2": fighter_links[0],
                "fighter_1_image": fighter_images[0],
                "fighter_2_image": fighter_images[1],
                "card_position": container.find("span", class_="text-xs11 md:text-xs10 uppercase font-bold").text.strip(),
                "fight_weight": container.find("span", class_="bg-tap_darkgold px-1.5 md:px-1 leading-[23px] text-sm md:text-[13px] text-neutral-50 rounded").text.strip(),
                "num_rounds": container.find("div", class_="div text-xs11").text.strip(),
            }
            fight_data_list.append(fight_data)

        return fight_data_list