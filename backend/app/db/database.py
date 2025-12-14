from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
import os

def _get_database_url() -> str:
    """
    Resolve DB URL for local/Docker and Railway.

    - Railway typically provides DATABASE_URL.
    - Local/Docker can use DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Railway/Heroku often use 'postgres://' which SQLAlchemy treats as deprecated.
        if database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://"):]
        return database_url

    # Support both Docker and local development
    # In Docker, use 'postgres' as hostname; locally, use 'localhost'
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "predictmma")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


URL_DATABASE = _get_database_url()

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