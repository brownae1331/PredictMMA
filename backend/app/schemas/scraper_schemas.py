from datetime import datetime, date
from re import S
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
    nickname: str | None
    height: str | None
    weight: str | None
    reach: str | None
    stance: str | None
    wins: int
    losses: int
    draws: int

class Fight(BaseModel):
    event_url: str
    fighter_1_url: str
    fighter_2_url: str
    match_number: int
    weight_class: str | None
    winner: bool
    method: str | None
    round: int | None
    time: str | None