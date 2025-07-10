from datetime import datetime
from pydantic import BaseModel

class Event(BaseModel):
    event_url: str
    event_title: str
    event_date: datetime
    event_location: str
    event_organizer: str

class Fight(BaseModel):
    event_url: str
    fight_idx: int
    fighter_1_link: str
    fighter_2_link: str
    fight_weight: str
    fight_winner: str
    fight_method: str
    fight_round: int
    fight_time: str