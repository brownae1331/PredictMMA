from pydantic import BaseModel
from datetime import datetime

class Event(BaseModel):
    id: int
    title: str
    date: datetime
    location: str
    location_flag: str
    organizer: str

class MainEvent(BaseModel):
    event_id: int
    event_title: str
    event_date: datetime
    fighter_1_id: int
    fighter_2_id: int
    fighter_1_name: str
    fighter_2_name: str
    fighter_1_nickname: str | None
    fighter_2_nickname: str | None
    fighter_1_image: str | None
    fighter_2_image: str | None
    fighter_1_ranking: str | None
    fighter_2_ranking: str | None