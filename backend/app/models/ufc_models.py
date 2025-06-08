from datetime import datetime
from typing import List
from pydantic import BaseModel

class MainEvent(BaseModel):
    fighter_1_link: str
    fighter_2_link: str
    fighter_1_name: str
    fighter_2_name: str
    fighter_1_image: str
    fighter_2_image: str
    fighter_1_rank: str
    fighter_2_rank: str

class EventSummary(BaseModel):
    event_url: str
    event_title: str
    event_date: datetime
    main_event: MainEvent | None

class Fight(BaseModel):
    fighter_1_link: str
    fighter_2_link: str
    fighter_1_name: str
    fighter_2_name: str
    fighter_1_image: str
    fighter_2_image: str
    fighter_1_rank: str
    fighter_2_rank: str
    fighter_1_flag: str
    fighter_2_flag: str
    fight_weight: str

class Event(BaseModel):
    event_url: str
    event_title: str
    event_date: datetime
    event_venue: str
    event_location: str
    event_location_flag: str
    event_fight_data: List[Fight] | None