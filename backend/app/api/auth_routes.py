from fastapi import APIRouter, HTTPException, status
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.db.database import db_dependency
from app.db.models import models
from app.core.utils.auth_utils import create_access_token, get_password_hash, verify_password

router = APIRouter()

@router.get("/test")
async def test_auth():
    """Test endpoint to check if auth routes are working."""
    return {"message": "Auth routes are working"}

@router.post("/test-db")
async def test_db(db: db_dependency):
    """Test database connection."""
    try:
        from sqlalchemy import text
        # Test database connection
        result = db.execute(text("SELECT 1 as test")).fetchone()
        return {"message": "Database connection working", "test": result[0]}
    except Exception as e:
        return {"message": "Database connection failed", "error": str(e)}

@router.post("/test-register-minimal")
async def test_register_minimal(db: db_dependency):
    """Test minimal registration logic."""
    try:
        # Test basic User creation without external dependencies
        test_user = models.User(
            username="testuser" + str(len("test")),
            hashed_password="test_hashed_password"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        return {"message": "Minimal user creation works", "user_id": test_user.id}
    except Exception as e:
        return {"message": "Minimal user creation failed", "error": str(e)}

@router.post("/test-password-hash")
async def test_password_hash():
    """Test password hashing functionality."""
    try:
        test_password = "testpassword123"
        password_bytes = test_password.encode('utf-8')

        return {
            "message": "Password length debug info",
            "password": test_password,
            "password_length_chars": len(test_password),
            "password_length_bytes": len(password_bytes),
            "password_bytes": list(password_bytes)[:20]  # First 20 bytes for debug
        }
    except Exception as e:
        return {"message": "Password debug failed", "error": str(e)}

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

    return {"message": "User registered successfully", "username": new_user.username}

@router.post("/login")
async def login(user: UserLogin, db: db_dependency):
    """
    Login for access token.
    """
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.id})
    return {"access_token": token, "token_type": "bearer"}