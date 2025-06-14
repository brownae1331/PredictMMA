from fastapi import APIRouter, HTTPException, status
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.db.database import db_dependency
from app.db.models import models
from app.core.auth_utils import create_access_token, get_password_hash, verify_password
from datetime import timedelta

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister, db: db_dependency):
    """
    Register a new user.
    """
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

@router.post("/login")
async def login(user: UserLogin, db: db_dependency):
    """
    Login for access token.
    """
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}