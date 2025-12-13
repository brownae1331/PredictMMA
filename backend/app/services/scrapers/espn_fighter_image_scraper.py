import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote

class ESPNFighterImageScraper:
    DEFAULT_NO_PHOTO_URL = "https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png"
    
    def __init__(self):
        self.base_url = "https://www.espn.co.uk"
        self.scraper = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }
    
    def search_fighter(self, fighter_name: str) -> BeautifulSoup:
        """Search for a fighter on ESPN by fetching the search results URL."""
        try:
            encoded_name = quote(fighter_name)
            search_url = f"{self.base_url}/search/_/q/{encoded_name}"
            
            response = self.scraper.get(search_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            return soup
            
        except Exception as e:
            print(f"Error searching for fighter: {e}")
            raise
    
    def search_fighter_api(self, fighter_name: str) -> dict:
        """Search for a fighter using ESPN's API."""
        try:
            encoded_name = quote(fighter_name)
            
            api_endpoints = [
                {
                    "url": "https://site.web.api.espn.com/apis/search/v2",
                    "params": {
                        "query": fighter_name,
                        "region": "uk",
                        "lang": "en",
                        "limit": 20,
                        "type": "player"
                    }
                },
                {
                    "url": "https://fan.api.espn.com/apis/search/v2",
                    "params": {
                        "query": fighter_name,
                        "limit": 20
                    }
                },
                {
                    "url": f"https://site.web.api.espn.com/apis/search/v1",
                    "params": {
                        "q": fighter_name,
                        "limit": 20
                    }
                }
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = self.scraper.get(endpoint["url"], params=endpoint["params"], headers=self.headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    if data:
                        return data
                except Exception:
                    continue
            
            return {}
        except Exception as e:
            print(f"Error searching API: {e}")
            return {}
    
    def get_fighter_image(self, fighter_name: str) -> str:
        """Get the image URL for the first MMA fighter found in search results."""
        api_data = self.search_fighter_api(fighter_name)
        
        if api_data:
            results = []
            if "results" in api_data:
                results = api_data["results"]
            elif "items" in api_data:
                results = api_data["items"]
            elif "data" in api_data:
                results = api_data["data"]
            elif isinstance(api_data, list):
                results = api_data
            
            for result in results:
                if not isinstance(result, dict):
                    continue
                
                if "contents" in result and isinstance(result["contents"], list):
                    for content in result["contents"]:
                        if not isinstance(content, dict):
                            continue
                        
                        uid = content.get("uid", "")
                        athlete_id = None
                        sport_id = None
                        
                        if uid:
                            uid_parts = uid.split("~")
                            for part in uid_parts:
                                if part.startswith("s:"):
                                    sport_id = part.split(":")[1]
                                elif part.startswith("a:"):
                                    athlete_id = part.split(":")[1]
                        
                        is_mma = False
                        
                        if sport_id == "3301":
                            is_mma = True
                        elif "sport" in content:
                            sport_obj = content["sport"]
                            if isinstance(sport_obj, dict):
                                sport_name = sport_obj.get("name", "").lower()
                                sport_slug = sport_obj.get("slug", "").lower()
                                if "mma" in sport_name or "mma" in sport_slug:
                                    is_mma = True
                        
                        if "league" in content:
                            league_obj = content["league"]
                            if isinstance(league_obj, dict):
                                league_slug = league_obj.get("slug", "").lower()
                                if league_slug == "mma":
                                    is_mma = True
                        
                        category = str(content.get("category", "")).lower()
                        display_name = str(content.get("displayName", "")).lower()
                        if "mma" in category or "mma" in display_name:
                            is_mma = True
                        
                        if is_mma and athlete_id:
                            image_url = (
                                content.get("image") or 
                                content.get("headshot") or 
                                content.get("headshotUrl") or
                                content.get("photo") or
                                content.get("picture")
                            )
                            
                            if image_url:
                                if isinstance(image_url, dict):
                                    image_url = image_url.get("default", "")
                                if image_url:
                                    return image_url
                            
                            image_url = f"https://a.espncdn.com/combiner/i?img=/i/headshots/mma/players/full/{athlete_id}.png"
                            return image_url
        
        soup = self.search_fighter(fighter_name)
        
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            href = link.get("href", "")
            if "/mma/fighter" in href.lower():
                match = re.search(r'/mma/fighter/_/id/(\d+)/', href)
                if match:
                    fighter_id = match.group(1)
                    image_url = f"https://a.espncdn.com/combiner/i?img=/i/headshots/mma/players/full/{fighter_id}.png"
                    return image_url
        
        return self.DEFAULT_NO_PHOTO_URL

if __name__ == "__main__":
    scraper = ESPNFighterImageScraper()
    print(scraper.get_fighter_image("Aaron Pico"))