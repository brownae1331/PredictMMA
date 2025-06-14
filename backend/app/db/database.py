from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

URL_DATABASE = "postgresql://postgres:Aeb130805@localhost:5432/predictmma"

engine = create_engine(URL_DATABASE)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]