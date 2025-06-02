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
                    return link
            except Exception as e:
                print(f"Error processing {link}: {e}")
            return None
        
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_link = {executor.submit(check_event_date, session, link): link for link in event_links}
                
                results = {}
                for future in as_completed(future_to_link):
                    link = future_to_link[future]
                    result = future.result()
                    results[link] = result
       
        upcoming_event_links = []
        for link in event_links:
            if results.get(link):
                upcoming_event_links.append(results[link])
        
        return upcoming_event_links
    
    def get_event_data(self, event_link: str) -> dict:
        """Scrapes the event data and returns the data"""
        try:
            response = requests.get(event_link, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            soup = BeautifulSoup(response.text, "html.parser")

            # Add null checks for all elements
            date_span = soup.find("span", string="Date/Time:")
            if not date_span:
                raise ValueError("Date/Time span not found")
            
            date_container = date_span.parent
            date_span = date_container.find("span", class_="text-neutral-700")
            
            if not date_span:
                raise ValueError("Date text span not found")
            
            date_text = date_span.text.strip()

            event_date_et = datetime.strptime(date_text, '%A %m.%d.%Y at %I:%M %p ET').replace(tzinfo=ZoneInfo('America/New_York'))
            event_date_bst = event_date_et.astimezone(ZoneInfo('Europe/London'))

            flag_div = soup.find("div", class_="div h-[14px]")
            flag_img = flag_div.find("img") if flag_div else None
            flag_src = None

            if flag_img and flag_img.get('src'):
                flag_src = flag_img['src']
                if flag_src.startswith('/'):
                    flag_src = f"https://www.tapology.com{flag_src}"

            title_element = soup.find("h2")
            venue_element = soup.find("span", string="Venue:")
            location_element = soup.find("span", string="Location:")
            
            if not title_element:
                raise ValueError("Event title not found")
            if not venue_element:
                raise ValueError("Venue not found")
            if not location_element:
                raise ValueError("Location not found")

            event_data = {
                "event_title": title_element.text.strip(),
                "event_date": event_date_bst.isoformat(),
                "event_venue": venue_element.parent.find("span", class_="text-neutral-700").text.strip(),
                "event_location": location_element.parent.find("span", class_="text-neutral-700").text.strip(),
                "event_location_flag": flag_src,
                "event_fight_data": self.get_fight_data(event_link)
            }

            return event_data
        except Exception as e:
            print(f"Error scraping event data from {event_link}: {e}")
            # Return a default structure instead of None
            return {
                "event_title": "Unknown Event",
                "event_date": datetime.now().isoformat(),
                "event_venue": "Unknown Venue",
                "event_location": "Unknown Location",
                "event_location_flag": None,
                "event_fight_data": []
            }
    
    def get_fight_data(self, event_link: str) -> list[dict]:
        """Scrapes the fight data and returns data for each fight and fighter"""
        response = requests.get(event_link, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        fight_data_list = []
        fight_containers = soup.find_all("div", class_="div flex flex-col mt-3 mb-4 md:mt-2.5 md:mb-2.5 w-full fullsize")

        for container in fight_containers:
            fighter_link_elements = container.find_all("a", class_="link-primary-red")
            
            seen_links = set()
            unique_fighter_links = []
            for link in fighter_link_elements:
                href = link.get('href')
                if href and href not in seen_links:
                    seen_links.add(href)
                    unique_fighter_links.append(link)
            fighter_link_elements = unique_fighter_links
            print(fighter_link_elements)
            fighter_links = [f"https://www.tapology.com{link['href']}" for link in fighter_link_elements]
            fighter_names = [link.text.strip() for link in fighter_link_elements]
            fighter_images = [img['src'] for img in container.find_all("img", class_="w-[77px] h-[77px] md:w-[104px] md:h-[104px] rounded")]

            fight_data = {
                "fighter_1_link": fighter_links[0],
                "fighter_2_link": fighter_links[1],
                "fighter_1_name": fighter_names[0],
                "fighter_2_name": fighter_names[1],
                "fighter_1_image": fighter_images[0],
                "fighter_2_image": fighter_images[1],
                "card_position": container.find("span", class_="text-xs11 md:text-xs10 uppercase font-bold").text.strip(),
                "fight_weight": container.find("span", class_="bg-tap_darkgold px-1.5 md:px-1 leading-[23px] text-sm md:text-[13px] text-neutral-50 rounded").text.strip(),
                "num_rounds": container.find("div", class_="div text-xs11").text.strip(),
            }
            fight_data_list.append(fight_data)

        return fight_data_list