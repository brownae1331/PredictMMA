from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
import os

URL_DATABASE =  "postgresql://postgres:postgres@postgres:5432/predictmma" 

engine = create_engine(
    URL_DATABASE,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]