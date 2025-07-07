from datetime import datetime
from pydantic import BaseModel

class Event(BaseModel):
    event_url: str
    event_title: str
    event_date: datetime
    event_location: str
    event_organizer: str