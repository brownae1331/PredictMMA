from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

class Event(BaseModel):
    url: str
    title: str
    date: datetime
    location: str
    organizer: str

class Fighter(BaseModel):
    url: str
    name: str
    nickname: str
    record: str
    country: str
    city: str
    age: int
    dob: Optional[date]
    height: str
    weight_class: str
    association: str

class Fight(BaseModel):
    event_url: str
    fighter_1_url: str
    fighter_2_url: str
    match_number: int
    weight_class: str
    winner: str
    method: str
    round: int
    time: str 