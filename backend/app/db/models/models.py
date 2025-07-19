from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime(timezone=True))
    location = Column(String)
    organizer = Column(String)

    fights = relationship("Fight", back_populates="event", cascade="all, delete-orphan")

class Fighter(Base):
    __tablename__ = "fighters"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    nickname = Column(String)
    image_url = Column(String)
    record = Column(String)
    ranking = Column(String)
    country = Column(String)
    city = Column(String)
    age = Column(Integer)
    dob = Column(Date)
    height = Column(String)
    weight_class = Column(String)
    association = Column(String)

    predictions = relationship("Prediction", back_populates="fighter", cascade="all, delete-orphan")

class Fight(Base):
    __tablename__ = "fights"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    fighter_1_id = Column(Integer, ForeignKey("fighters.id", ondelete="CASCADE"), nullable=False)
    fighter_2_id = Column(Integer, ForeignKey("fighters.id", ondelete="CASCADE"), nullable=False)
    match_number = Column(Integer, nullable=False)
    weight_class = Column(String)
    winner = Column(String)
    method = Column(String)
    round = Column(Integer)
    time = Column(String)

    __table_args__ = (
        UniqueConstraint("event_id", "match_number", name="uix_event_match_number"),
    )

    event = relationship("Event", back_populates="fights")
    fighter_1 = relationship("Fighter", foreign_keys=[fighter_1_id])
    fighter_2 = relationship("Fighter", foreign_keys=[fighter_2_id])
    predictions = relationship("Prediction", back_populates="fight", cascade="all, delete-orphan")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fight_id = Column(Integer, ForeignKey("fights.id", ondelete="CASCADE"), nullable=False)
    fighter_id = Column(Integer, ForeignKey("fighters.id", ondelete="CASCADE"), nullable=False)
    method = Column(String, nullable=False)
    round = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "fight_id", name="uix_user_fight"),
    )

    user = relationship("User", back_populates="predictions")
    fight = relationship("Fight", back_populates="predictions")
    fighter = relationship("Fighter", back_populates="predictions")