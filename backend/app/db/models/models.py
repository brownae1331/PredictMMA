from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

class Prediction(Base):
    __tablename__ = 'predictions'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    event_url = Column(String, primary_key=True)
    fight_id = Column(String, primary_key=True)
    fight_idx = Column(Integer)
    fighter_prediction = Column(String)
    method_prediction = Column(String)
    round_prediction = Column(Integer, nullable=True)

class Event(Base):
    __tablename__ = 'events'

    event_url = Column(String, primary_key=True)
    event_title = Column(String)
    event_date = Column(DateTime(timezone=True))
    event_location = Column(String)
    event_organizer = Column(String)